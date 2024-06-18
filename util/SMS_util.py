import requests as r
from util import config_util as cutil, \
log_util as lutil

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List

def getPhoneArray() -> List[List[str]]:


  # If modifying these scopes, delete the file token.json.
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID of a sample document.
  SHEETS_ID = cutil.get_config_item("sheet_id")



  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("sheet_token.json"):
    creds = Credentials.from_authorized_user_file("sheet_token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          r"sheet_credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("sheet_token.json", "w") as token:
      token.write(creds.to_json())

  try:
    array = []
    service = build("sheets", "v4", credentials=creds)

    # Retrieve the documents contents from the Docs service.
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=SHEETS_ID, range="B:D").execute()
    
    values = result.get("values", [])


    for i in range(len(values)-1):
      array.append(values[i+1])
    
    return array
  except HttpError as err:
    print(err)




def sendSMSreminder(body, recipient):
  phoneNum = getPhone(recipient)
  if len(phoneNum) == 0:
    lutil.log(f"Error: No phone number available, skipping SMS for {recipient}")
    return
    
  response = r.post("https://textbelt.com/text", {
    "phone":phoneNum[0],
    "message":body,
    "key": cutil.get_config_item("textbelt_key")
  })
  data = response.json()
  if data["success"] == True:
    quota = data["quotaRemaining"]
    lutil.log(f"Successfully sent a message to {recipient}. There are {quota} messages left before the next billing!")




def getPhone(name: str):
  phones = getPhoneArray()
  
  return [i[2] for i in phones if f"{i[0]} {i[1]}".lower() == name.lower()]
  