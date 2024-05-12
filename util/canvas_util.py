import requests
import json
from util import config_util

BASE_URL = "https://dexterschools.instructure.com/api/v1"

def get_notification_course_id():
    return config_util.get_config_item("default_canvas_course")

def send_announcement(course_id, title, message, is_published=True):
    token = config_util.get_config_item("canvas_token")

    PARAMS = {
            "access_token": token,
            "title": title,
            "message": message,
            "published": is_published,
            "is_announcement": True
        }

    r = requests.post(f"{BASE_URL}/courses/{course_id}/discussion_topics", PARAMS)
    return r.json()

def send_reminder(body, subject, recipient):  #Function that uses the information from notif util and sends it out
    token = config_util.get_config_item("canvas_token")

    PARAMS = {
        "subject": subject,
        "access_token": token,
        "body": body,
        "recipients": get_id(recipient),
        "force_new": True  #Creates a new conversation every time (Just to make sure it will always notify)
    }

    r = requests.post(f"{BASE_URL}/conversations", PARAMS)
    return r.json()
def print_reminder(body, subject, recipient): #Again, just a test function
    print(subject)
    print(body)
    print(recipient)

 #This function is finds a corresponding name in the json file and returns their canvas ID, since that's how messages get 
 #sent in Canvas. The JSON file was made by my own script I created, which I will put into the utilities folder. 

def get_id(student: str): 

    with open("ids.json") as f:  #JSON file name is ids for ID's
        ids = json.load(f)
        f.close()

    for i in range(len(ids)): #For each dictionary 
        if (ids[i]["name"] == student):
            return ids[i]["id"]
    return -1 #If there is no name that corresponds, sends -1