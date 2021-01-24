import requests
from pprint import pprint

def update_page(dic, address):
    print('update_page function started')
    print(len(dic['question_id_lst']))
    address += '/gather_questions'

    requests.post(address,json=dic)
    
