import requests as r
import config_util as cutil
import json

PARAMS = {"access_token": cutil.get_config_item("canvas_token"),  
          "per_page":99, #I had to paginate the API because there are a lot of students in the NHS course
          "page":1, 
          "enrollment_type[]":["student","ta"] #Includes only students and TA's, not observers or teachers.
          }

output = [] #Creates dictionaries for each student (name and ID only)

req = r.get("https://dexterschools.instructure.com/api/v1/courses/2539/users", PARAMS)  #Gets the first page of students
data = req.json()

while len(data) > 0:   #Data has a length of 0 when the page no longer contains students, so the loop ends after there are no more students to add
    req = r.get("https://dexterschools.instructure.com/api/v1/courses/2539/users", PARAMS) 
    data = req.json() 
    for i in range(len(data)): #For each student in the page
        name = data[i]["name"]
        id = data[i]["id"]
        output.append(dict(name=data[i]["name"],id=data[i]["id"]))  #Adds the dictionary
    PARAMS["page"] += 1 #next page


with open("ids.json", "w") as outfile:  #Opens up the ids.json file. Not sure how to create one if there isnt one so we can discuss that
    outfile.write(json.dumps(output, ensure_ascii=False, indent=4))  #puts the output in the json file, the last 2 args are just for aesthetic purposes in the file











 
   