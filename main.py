print('Loading modules, might take some seconds...')
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
import os
from src.main_script import start_script
import shelve
import sys
from tkinter import TOP, W, RIGHT
import requests


window = tk.Tk()
window.title('Collab Desktop')
window.geometry()
window.title('Moodle Collab Desktop')
reset_db_frame = tk.Frame()
chromedriver_frame =tk.Frame()
settings_frame = tk.Frame()
submit_frame = tk.Frame()
string_var = tk.StringVar(value='Off')


address = 'http://139.162.161.55'
# address = 'http://127.0.0.1:5000'


with shelve.open('user_db') as db:


    def open_chromedriver():
        file = askdirectory() 
        if file is not None: 
            db['chrome_driver_dir_path'] = os.path.abspath(file)
            chrome_label = tk.Label(text=f'{os.path.basename(file)} loaded!', master=chromedriver_frame)
            chrome_label.pack()
  

    try:
        chrome_driver_dir_path = db['chrome_driver_dir_path']
        if chrome_driver_dir_path == None:
            raise KeyError

    except KeyError:
        btn = tk.Button(
                master=chromedriver_frame, 
                text = 'Select Chromedriver Path',
                command = open_chromedriver,
                width= 20,
                fg='black')
        btn.pack()

    try:
        if db['username'] == None:
            raise KeyError
        usr = db['username']
        welcome_label = tk.Label(text=f"Welcome {usr}!", master=settings_frame)
        welcome_label.pack()
        
        
    except KeyError:
        username_label = tk.Label(text="Username", master=settings_frame)
        username = tk.Entry(width=20, master=settings_frame)
        username_label.pack()
        username.pack()

    google_form_value = tk.IntVar()

    c1 = tk.Checkbutton(master=settings_frame, text='Hosted on Google Forms?',variable=google_form_value, onvalue=1, offvalue=0)
    c1.pack(side=TOP, anchor=W)


    def start_session():

        try:
            if db['username'] == None:
                raise KeyError
            usr = db['username']
        except KeyError:
            db['username'] = username.get()


        MOODLECOLLABPLATFORM = 1
        GOOGLEFORM = google_form_value.get()

        chrome_driver_dir_path = db['chrome_driver_dir_path']


        # USE REQUESTS TO RETRIEVE REGISTERED USERS
        r = requests.get(address + '/get_user_list')
        registered_users = r.json()['data']


        # IF USER NOT IN REGISTERED USERS RESETS USERNAME AND CLOSES THE APPLICATION
        usr =  db['username']
        if usr not in registered_users:
            print('Not a valid user')
            db['username'] = None
            sys.exit()


        else:
            start_script(
                usr,
                MOODLECOLLABPLATFORM,
                GOOGLEFORM,
                chrome_driver_dir_path,
                address,
                window
            )


    submit_info_btn = tk.Button(
                master=submit_frame, 
                text ='Start Session',
                command = start_session,
                width= 18,
                )

    submit_info_btn.pack()


    def reset_db():
        db['chrome_driver_dir_path'] = None
        db['username'] = None
        db['pdf_path'] = None
        sys.exit()
        

    reset_db_btn = tk.Button(
            master=reset_db_frame, 
            text ='reset db',
            command = reset_db
            )
    reset_db_btn.grid()



    reset_db_frame.pack()
    chromedriver_frame.pack()
    settings_frame.pack()
    submit_frame.pack(pady=15,padx=10)


    if __name__ == '__main__':

        window.mainloop()
        
