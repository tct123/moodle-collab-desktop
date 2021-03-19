
import requests
import re
from platform import system as OS_system

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import shelve

import os
import sys
from src.server_communication import send_questions_to_collab, ready_to_go, loading_questions_alert
from pprint import pprint
import subprocess

from time import perf_counter

import json
import threading





def get_unique_question_id(question, related_answers):
    '''
    DOCSTRING:
    returns an unique question_id
    '''
    strp_question = question.replace(' ','_').lower()
    answers_words = []
    for answer in related_answers:
        answers_words += answer.split()
    answers_words.sort(reverse=True)
    answers_words = [answer_word.lower() for answer_word in answers_words if answer_word.isalnum()] # POTENZIALE PUNTO DI ERRORE!
    try:
        last_answr_words = answers_words[:3]    
    except:
        last_answr_words= answers_words[:2]

    id_answer_words = '_'.join(last_answr_words)
    question_id = strp_question + '_' + id_answer_words

    return question_id




def save_to_textfile(i, question, answers, path=''):

    question_transcription = f'Q{i}: {question}\n'
    answers_transcription = ['- ' + answer + '\n' for answer in answers]
    filename = os.path.join(path,'examfile.txt')
    try:
        with open(filename,'a') as textfile:
            textfile.write(question_transcription)
            textfile.writelines(answers_transcription)
            textfile.flush()
    except Exception as e:
        print('[ERROR] while saving to file')
        print(e)
        quit()
    



def retrieve_chromedriver(chrome_driver_dir_path):
    chromedrivers = os.listdir(chrome_driver_dir_path)
    chromedrivers.reverse() # to start from the latest available chromedriver and avoid hitting hidden files

    for chromedriver in chromedrivers:
        print(chromedriver)
        try:
            driver_path = os.path.join(chrome_driver_dir_path, chromedriver)
            print(driver_path)
            driver = webdriver.Chrome(driver_path)
            break
        except:
            print('[WARNING] Error while trying to set up chromedriver, trying with another version')

    print('[SUCCESS] Chromedriver set up successfully')
        
        

    return driver




def start_script(username, MOODLECOLLABPLATFORM, GOOGLEFORM, chrome_driver_dir_path, address, window):

    window.destroy()


    # SELENIUM STUFF:
            
    if GOOGLEFORM == 1:
        moodle_page = 'https://docs.google.com/forms/d/e/1FAIpQLSc_twwFSOZv5QMNf4V0R_LIhgGXROumAWgLWcPl-AYiEFTEbw/viewform?usp=sf_link'
    
    else:
        moodle_page = 'https://www.infomedct.ro'
        

    driver = retrieve_chromedriver(chrome_driver_dir_path)
    print('Selenium graphical mode Initialized')
    driver.get(moodle_page)




    def gather_questions_g_forms():
        
        question_data = []
        content_boxes = driver.find_elements_by_xpath('//div[@class="m2"]')
        print(f'Num of questions found: {len(content_boxes)}')

        if len(content_boxes) != 0:


            for i in range(len(content_boxes)):
                i += 1

                try:
                    question = driver.find_element_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[1]/div[1]/div[1]')
                    answers = driver.find_elements_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[2]/div/div/span/div/div/label')

                    if len(answers) == 0:
                        answers = driver.find_elements_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[2]/div//label//span')

                except Exception as e:
                    print('Unexpected error during gathering of data from the question divs, try to reload again... ')
                    print(e)
                    continue

                question_txt = question.text.replace('"','’’').replace("'",'’')
                answers_txt = [answer.text.replace('"',"’’") for answer in answers if answer.text !='']
                question_id = get_unique_question_id(question_txt, answers_txt)

                question_information = {
                    'index': i,
                    'question_id': question_id,
                    'question_text': question_txt,
                    'answers_lst': answers_txt
                }
                question_data.append(question_information)
            return question_data
        else:
            return None


    def gather_questions_moodle():

        '''
        DOCSTRING:
        Returns a list of the questions found or None if no questions have been detected in the page

        '''

        question_data = []
        content_boxes = driver.find_elements_by_xpath('//div[contains(@class,"formulation clearfix")]')

        print(f'Num of questions found: {len(content_boxes)}')

        if len(content_boxes) != 0:

            threading.Thread(target=loading_questions_alert, args=(username, address, len(content_boxes))).start()

            for i in range(len(content_boxes)):
                
                i += 1
                
                try:
                    true_index = driver.find_element_by_xpath(f'(//span[contains(@class,"qno")])[{i}]').text
                    question = driver.find_element_by_xpath(f'(//div[@class="formulation clearfix"])[{i}]/div[@class="qtext"]')
                    answer_block = f'(//div[@class="formulation clearfix"])[{i}]/div[@class="ablock"]'
                    answers = driver.find_elements_by_xpath(f'{answer_block}//label[contains(@for,"answer")]//div[contains(@class,"flex-fill")]|{answer_block}//label[contains(@for,"choice")]//p[@dir="ltr"]')

                except Exception as e:
                    print('Unexpected error during gathering of data from the question divs, try to reload again... ')
                    print(e)
                    continue

                question_txt = question.text.replace('"','’’').replace("'",'’')
                answers_txt = [answer.text.replace('"',"’’") for answer in answers if answer.text !='']
                question_id = get_unique_question_id(question_txt, answers_txt)


                question_information = {
                    'index': true_index,
                    'question_id': question_id,
                    'question_text': question_txt,
                    'answers_lst': answers_txt
                }
                question_data.append(question_information)
            return question_data
        else:
            return None



    def process_data(gather_questions_funct):

        ready_to_go(username, address)
        while True:

            current_url = driver.current_url
            try:
                t_start = perf_counter()
                try:
                    driver.implicitly_wait(2)
                    if driver.current_url == current_url:
                        question_data = gather_questions_funct()
                    else:
                        continue

                except:

                    print('2nd Try...')
                    driver.implicitly_wait(2)
                    if driver.current_url == current_url:
                        question_data = gather_questions_funct()
                    else:
                        continue

                t_end = perf_counter()
                print(f'elapsed time: {t_end - t_start}')

                if len(question_data) == 0:
                    continue


                result = {
                    'user_id': username,
                    'question_data': question_data
                }

                # SEND DATA TO COLLAB
                
                try:
                    send_questions_to_collab(result, address)
                    print('Data correctly sent to Moodle Collab')

                except Exception:
                    try:
                        send_questions_to_collab(result, address)
                        print('Data correctly sent to Moodle Collab')

                    except Exception:
                        print('[ERROR] Couldn\'t connect to Moodle Collab')
                        continue

            except:
                pass

            finally:

                # wait for url_change
                WebDriverWait(driver, 36000).until_not(EC.url_to_be(current_url))
                print('[!]Change of page detected')


    gather_questions_funct = gather_questions_moodle if GOOGLEFORM != 1 else gather_questions_g_forms
    process_data(gather_questions_funct)






        

    



    
        
      
    
    

            
            
        
            
        
            
        
        
        
        
        
        



