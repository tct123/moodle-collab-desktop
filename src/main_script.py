
import requests
import re
from platform import system as OS_system

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import shelve

import os
import sys
from src.server_communication import update_page
from pprint import pprint
import subprocess


from time import perf_counter



def unique_question_id_lst(dic):
    '''
    returns a list containing all uniques question_id for the scraped page

    '''
    question_id_lst = []

    for question, answers in dic.items():
        strp_question = question.replace(' ','_').lower()
        

        
        answers_words = []
        
        for answer in answers:
            answers_words += answer.split()
        
        answers_words.sort(reverse=True)
        answers_words = [answer_word.lower() for answer_word in answers_words if answer_word.isalnum()] # POTENZIALE PUNTO DI ERRORE!
        try:
            last_answr_words = answers_words[:3]    
        except:
            last_answr_words= answers_words[:2]    
            
        id_answer_words = '_'.join(last_answr_words)

        question_id = strp_question + '_' + id_answer_words
        question_id_lst.append(question_id)

    return question_id_lst
        





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
    

def dic_to_lst(dic):
    '''
    REQUIRED TO LOAD QUESTIONS IN A LIST TO PASS TO s.updateColumn FUNCTION
    '''
    result = []
    for question, answers in dic.items():
        answers.insert(0, question)
        answers.append('')
        result.extend(answers)
    return result



def retrieve_chromedriver_v2(chrome_driver_dir_path):
    if OS_system() == 'Windows':
        try:
            driver_path = os.path.join(chrome_driver_dir_path, 'chromedriver_86_windows.exe' )
            driver = webdriver.Chrome(driver_path)

        except:
            print('[WARNING] Error while trying to set up chromedriver, trying with another version')
            driver_path = os.path.join(chrome_driver_dir_path, 'chromedriver_87_windows.exe' )
            driver = webdriver.Chrome(driver_path)

    else:
        try:
            driver_path = os.path.join(chrome_driver_dir_path, 'chromedriver_86_mac')
            driver = webdriver.Chrome(driver_path)

        except:
            print('[WARNING] Error while trying to set up chromedriver, trying with another version')
            driver_path = os.path.join(chrome_driver_dir_path, 'chromedriver_87_mac')
            driver = webdriver.Chrome(driver_path)
    
    print('[SUCCESS] Chromedriver set up successfully')
    return driver



    
    


def start_script(username, MOODLECOLLABPLATFORM, GOOGLEFORM, chrome_driver_dir_path, address, window):

    window.destroy()



    # SELENIUM STUFF:
            
    if GOOGLEFORM == 1:
        moodle_page = 'https://docs.google.com/forms/d/e/1FAIpQLSc_twwFSOZv5QMNf4V0R_LIhgGXROumAWgLWcPl-AYiEFTEbw/viewform?usp=sf_link'
    
    else:
        moodle_page = 'https://www.infomedct.ro'
        
    # driver = retrieve_chromedriver()

            
    
    driver = retrieve_chromedriver_v2(chrome_driver_dir_path)
    print('Selenium graphical mode Initialized')
    driver.get(moodle_page)

    def gather_questions_g_forms():
        
        true_indexes = []
        content_boxes = driver.find_elements_by_xpath('//div[@class="m2"]')
        print(f'Num of questions found: {len(content_boxes)}')

        if len(content_boxes) != 0:

            QADict = {}

            for i in range(len(content_boxes)):
                i += 1
                true_indexes.append(i)


                try:
                    question = driver.find_element_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[1]/div[1]/div[1]')
                    answers = driver.find_elements_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[2]/div/div/span/div/div/label')

                    if len(answers) == 0:
                        answers = driver.find_elements_by_xpath(f'(//div[@class="m2"])[{i}]/div[1]/div[2]/div//label//span')

                    question_txt = question.text.replace('"','’’')
                    question_txt = question_txt.replace("'",'’')



                except Exception as e:
                    print('Unexpected error during gathering of data from the question divs, try to reload again... ')
                    print(e)
                    continue
                
                answers_txt = [answer.text.replace('"',"’’") for answer in answers if answer.text !='']

                QADict[question_txt] = answers_txt


            return QADict, true_indexes


        else:
            return None
        

    def gather_questions_moodle():

        true_indexes = []
        content_boxes = driver.find_elements_by_xpath('//div[contains(@class,"formulation clearfix")]')
        print(f'Num of questions found: {len(content_boxes)}')

        if len(content_boxes) != 0:

            QADict = {}
            
            for i in range(len(content_boxes)):
                
                i += 1
                
                try:
                    true_index = driver.find_element_by_xpath(f'(//span[contains(@class,"qno")])[{i}]').text
                    true_indexes.append(true_index)

                    
                    question = driver.find_element_by_xpath(f'(//div[contains(@class,"formulation clearfix")])[{i}]/div[@class="qtext"]')
                    answers = driver.find_elements_by_xpath(f'(//div[contains(@class,"formulation clearfix")])[{i}]//label[contains(@for,"answer") and not(contains(text(),"Clear my choice"))]//p') 

                    question_txt = question.text.replace('"','’’')
                    question_txt = question_txt.replace("'",'’')


                except Exception as e:
                    print('Unexpected error during gathering of data from the question divs, try to reload again... ')
                    print(e)
                    continue

                if len(answers) == 0:
                    answers = driver.find_elements_by_xpath(f'(//div[contains(@class,"formulation clearfix")])[{i}]//label[contains(@for,"answer")and not(contains(text(),"Clear my choice"))]/span[not(contains(@class,"answernumber"))]')

                if len(answers) == 0:
                    # MULTIPLE SOLUTION QUESTIONS
                    answers = driver.find_elements_by_xpath(f'(//div[contains(@class,"formulation clearfix")])[{i}]//label[contains(@for,"choice")and not(contains(text(),"Clear my choice"))]//p') 
                    question_txt = question.text + ' [MULTIPLE SOLUTION]'
                if len(answers) == 0:
                    answers = driver.find_elements_by_xpath(f'(//div[contains(@class,"formulation clearfix")])[{i}]//label[contains(@for,"choice")and not(contains(text(),"Clear my choice"))]/span[not(contains(@class,"answernumber"))]')

                answers_txt = [answer.text.replace('"',"’’") for answer in answers if answer.text !='']

                try: 
                    QADict[question_txt]
                    question_txt += f' ({true_index})'
                except KeyError:
                    pass
                    
                QADict[question_txt] = answers_txt


            return QADict, true_indexes

        else:
            return None
  
    
    def process_data(gather_questions_funct):


        while True:

            current_url = driver.current_url

            try:

                t_start = perf_counter()

                QADict, true_indexes = gather_questions_funct()

                t_end = perf_counter()
                print(f'elapsed time: {t_end - t_start}')


                question_id_lst = unique_question_id_lst(QADict)

                result_dic = {
                    'username': username,
                    'question_id_lst': question_id_lst,
                    'true_indexes': true_indexes,
                    'q_and_a_text': QADict
                }

                # SEND DATA TO COLLAB
                
                try:
                    update_page(result_dic, address)
                    print('Data correctly sent to Moodle Collab')

                except Exception:

                    try:
                        update_page(result_dic, address)
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






        

    



    
        
      
    
    

            
            
        
            
        
            
        
        
        
        
        
        



