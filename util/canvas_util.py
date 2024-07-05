import requests
from util import config_util, \
log_util as lutil

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

def send_reminder(body, subject, recipient, students):  #Function that uses the information from notif util and sends it out
    lutil.log("Attempting to send reminder...")
    token = config_util.get_config_item("canvas_token")

    student_id = get_id(students, recipient)
    if student_id == None:  
        lutil.log(f"Unable to send message.")
        return

    PARAMS = {
        "subject": subject,
        "access_token": token,
        "body": body,
        "recipients": student_id,
        "force_new": True  #Creates a new conversation every time (Just to make sure it will always notify)
    }

    r = requests.post(f"{BASE_URL}/conversations", PARAMS)
    lutil.log(f"Successfully sent a canvas message to {recipient}")
    return r.json()


def print_reminder(body, subject, recipient): #Again, just a test function
    print(subject)
    print(body)
    print(recipient)

def get_id(students, name: str): 
    lutil.log(f"Beginning search for {name}'s Canvas ID")
    for student in students: #For each dictionary 
        if (student.name == name):
            lutil.log(f"Successfully obtained the ID: {student.id}")
            return student.id 
    lutil.log("Unable to locate ID for this user, skipping...")
    return None #If there is no name that corresponds, sends None