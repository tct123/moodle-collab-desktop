import requests
from pprint import pprint

def send_questions_to_collab(result, address):
    print('send_questions_to_collab function started')
    address += '/gather_questions'

    requests.post(address,json=result)
    
def ready_to_go(username, address):
    user_dic = {'username' : username}
    address += '/user_ready'
    requests.post(address,json=user_dic)

def loading_questions_alert(username, address, num_of_questions):
    print('loading_questions_alert function started')

    data = {
        'username':username,
        'num_of_questions': num_of_questions
    }
    address += '/loading_questions'
    r = requests.post(address, json=data)
    print(r.status_code)