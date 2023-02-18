from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from selenium import webdriver
import pandas as pd
from playwright._impl._api_types import TimeoutError


class SignUp:
    def __init__(self, title, author, description, roles):
        self.title = title
        self.author = author
        self.description = description
        self.roles = roles


class SignUpRole:
    def __init__(self, title, current, needed, location, date, start_time, end_time):
        self.title = title
        self.current = current
        self.needed = needed
        self.location = location
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
    
    def full(self): return self.current == self.needed

    def get_role_string(self):
        return f"Title: {self.title}" + "\n" + \
            f"   Status: {self.current}/{self.needed}" + "\n" + \
            f"   Location: {self.location}" + "\n" + \
            f"   Date: {self.date}" + "\n" + \
            f"   Time: {self.start_time} - {self.end_time}"


WHOLE_TITLE = ("h1", {"class": "signup--title-text ng-binding"})
WHOLE_AUTHOR = ("div", {"class": "pull-left signup--creator-name ng-binding"})
WHOLE_DESCRIPTION = ("p", {"class": "ng-binding", "data-ng-bind-html": "signupInfo.header.description"})

SIGNUP_TABLE = ("table", {"class": "table table-bordered date-sorted showsegments"})


def fix_signupgenius_url(url):
    if "signupgenius.com" not in url:
        return None


def get_dynamic_soup(url: str, retries) -> BeautifulSoup:
    current_try = 0
    soup = None
    while current_try < retries:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                soup = BeautifulSoup(page.content(), "html.parser")
                browser.close()

                if soup != None: break

                current_try += 1
        except TimeoutError:
            current_try += 1

    return soup


def get_page_data(url, retries):
    soup = get_dynamic_soup(url, retries)

    s_title = soup.find(WHOLE_TITLE[0], attrs=WHOLE_TITLE[1])
    s_author = soup.find(WHOLE_AUTHOR[0], attrs=WHOLE_AUTHOR[1])

    s_description_temp = soup.find(WHOLE_DESCRIPTION[0], attrs=WHOLE_DESCRIPTION[1])
    s_description = s_description_temp.find("p", attrs={"style": "text-align: inherit;"})
    description = None
    if s_description != None:
        description = s_description.text

    table = soup.find(SIGNUP_TABLE[0], SIGNUP_TABLE[1])
    data = pd.read_html(table.prettify(), displayed_only=False)

    table = data[0]
    
    slot_label = "Available Slot"
    if slot_label not in table.columns:
        slot_label = "Volunteer"
    for i in range(len(table[slot_label])):
        s = table[slot_label][i]
        if(str(s) == "nan"): table = table.drop(i)

    table = table.reset_index()
    table = table.drop(columns=["index"])
    return {
            "table": table,
            "title": s_title.text,
            "author": s_author.text,
            "description": description
        }


def get_signup_data(url: str, retries):
    data = get_page_data(url, retries)

    table = data["table"]
    print(data["table"])

    roles = []
    for i in range(len(table.index)):
        row = table.loc[i]

        date = str(row["Date"]).split("  ")[0]

        location = row["Location"].split("  ")[0]
        if str(location) == "nan":
            location = None

        full_time = str(row["Time"]).split("  ")
        start_time = full_time[0].replace("-", "")
        end_time = full_time[1]

        slot_label = "Available Slot"
        if slot_label not in row:
            slot_label = "Volunteer"

        slot_array = str(row[slot_label]).split("  ")
                
        title = slot_array[1]
        
        current = 0
        needed = 0
        status = slot_array[2].split(" ")
        if status[0] == "All":
            current = int(status[1])
            needed = current
        elif status[1] == "slots":
            needed = int(status[0])
        else:
            current = int(status[0])
            needed = int(status[2])

        roles.append(SignUpRole(title, current, needed, location, date, start_time, end_time))

    return SignUp(data["title"], data["author"], data["description"], roles)

