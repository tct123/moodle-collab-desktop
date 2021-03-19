import requests


def telegram_bot_sendtext(username):

    try:

        bot_token = '1725506923:AAGsgSLK0Omw2WjEwhtQ982my4m-TVzeP0c'
        bot_chatID = '169333018'
        message=f'[{username}] Connected to Collab Desktop'
        send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chatID}&text={message}'
        response = requests.get(send_text)
        return response.json()

    except Exception as e:
        print(e)
        return None


    





