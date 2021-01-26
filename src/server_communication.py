import requests
from pprint import pprint

def send_questions_to_collab(dic, address):
    print('send_questions_to_collab function started')
    print(len(dic['question_id_lst']))
    address += '/gather_questions'

    requests.post(address,json=dic)
    
def ready_to_go(username, address):
    user_dic = {'username' : username}
    address += '/user_ready'
    requests.post(address,json=user_dic)

