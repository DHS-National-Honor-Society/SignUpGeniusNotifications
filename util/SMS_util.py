import requests as r
from util import config_util as cutil, \
log_util as lutil
import json
def sendSMSreminder(body, recipient):
    phoneNum = getPhone(recipient)
  
    response = r.post("https://textbelt.com/text", {
    "phone":"7348813725",
    "message":body,
    "key": cutil.get_config_item("textbelt_key")
  })
    lutil.log(response.json())


def getPhone(name: str):
  with open("student_numbers.json","r") as file:
    numbers = json.load(file)
    return [i['phone'] for i in file if i['name'] == name]