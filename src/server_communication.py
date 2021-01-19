import requests
from pprint import pprint

def update_page(dic, address):
    print('update_page function started')
    pprint(len(dic['question_id_lst']))
    address += '/home'

    requests.post(address,json=dic)
    
