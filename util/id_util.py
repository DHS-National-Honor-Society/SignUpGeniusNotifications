import requests as r
from util import config_util as cutil, \
log_util as lutil
import json

class Student:
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name


def get_student_array():
    lutil.log("Beginning fetch for students and TA's...")

    PARAMS = {"access_token": cutil.get_config_item("canvas_token"),  
            "per_page":99, #I had to paginate the API because there are a lot of students in the NHS course
            "page":1, 
            "enrollment_type[]":["student","ta"] #Includes only students and TA's, not observers or teachers.
            }
    students = [] 

    req = r.get("https://dexterschools.instructure.com/api/v1/courses/2539/users", PARAMS)
    data = req.json()

    while len(data) > 0: 
        req = r.get("https://dexterschools.instructure.com/api/v1/courses/2539/users", PARAMS) 
        data = req.json() 
        for i in range(len(data)): #For each student in the page
            students.append(Student(data[i]["name"],data[i]["id"])) #Adds the dictionary
        PARAMS["page"] += 1 #next page
    lutil.log(f"Successfully obtained {len(students)} students and TA's and their Canvas ID's.")
    return students








 
   