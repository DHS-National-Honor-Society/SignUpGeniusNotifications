from util import log_util as lutil, config_util
import datetime
import requests as r
import json
import re
import math



class SignUp:
    def __init__(self, url, id, title, author, general_start_time, general_end_time):
        self.url = url
        self.id = id
        self.title = title
        self.author = author

        self.general_start_time = general_start_time
        self.general_end_time = general_end_time

        self.roles = []


    def __str__(self):
        return f"SignUp title: {self.title} \n SignUp creater: {self.author} \n SignUp Roles: {self.roles}"

    def get_url_id(self):
        return self.url.split("https://www.signupgenius.com/go/")[1]

    def from_json(json_object):
        roles = []
        for role in json_object["roles"]: roles.append(SignUpRole.from_json(role))

        signup = SignUp(
            json_object["url"],
            json_object["id"],
            json_object["title"],
            json_object["author"],
            json_object["start_time"],
            json_object["end_time"]
        )
        
        signup.set_roles(roles)

        return signup

    def to_json(self):
        roles_json_array = []
        for role in self.roles:
            roles_json_array.append(role.to_json())

        return {
                "url": self.url,
                "id": self.id,
                "title": self.title,
                "author": self.author,
                "start_time": self.general_start_time,
                "end_time": self.general_end_time,
                "roles": roles_json_array
            }

    def set_roles(self, roles):
        for role in roles:
            if role.start_time == 0:
                role.start_time = self.general_start_time

            if role.end_time == 0:
                role.end_time = self.general_end_time
                
        self.roles = roles

    def get_roles(self,
                  days_out=None,
                  days_from=0,
                  hours_out=None,
                  hours_from=0,
                  include_full=True,
                  include_ended=True):
        roles = self.roles

        if roles:
            if days_out:
                roles = [r for r in roles if r.get_days_until() <= days_out and
                         r.get_days_until() >= days_from]
            elif hours_out:
                roles = [r for r in roles if r.get_hours_until() <= hours_out and
                         r.get_hours_until() >= hours_from]

            if not include_full:
                roles = [r for r in roles if not r.full()]

            if not include_ended:
                roles = [r for r in roles if not r.has_ended()]

        return roles
    
    
    

    def get_signup_message(self,
                           days_out=None,
                           days_from=0,
                           hours_out=None,
                           hours_from=0,
                           include_full=True,
                           include_time_detail=False):
        if not days_out and not hours_out:
            return None
        
        message = ""

        roles = self.get_roles(days_out=days_out,
                               days_from=days_from,
                               hours_out=hours_out,
                               hours_from=hours_from,
                               include_full=include_full)

        full_roles_seperated = [r for r in roles if r.full()]
        roles = [r for r in roles if not r.full()]

        if roles or full_roles_seperated:
            message += "\n<hr>"
        else:
            return message
        
        when_string = ""
        if include_time_detail:
            if days_out:
                when_string = f" in the next {days_out if days_out > 1 else ''} day{'s'[:days_out^1]}"
            elif hours_out:
                when_string = f" in the next {hours_out if hours_out > 1 else ''} hour{'s'[:hours_out^1]}"

        if roles:
            whole_needed = 0
            not_full_update = []
            for r in roles:
                not_full_update.append("- " + r.get_notification_role_string())
                whole_needed += r.needed
            
            not_full_update_str = "\n".join(not_full_update)
            not_full_update_str = f"<blockquote>{not_full_update_str}</blockquote>"

            not_full_title = f"'{self.title}' has {whole_needed} slot{'s'[:whole_needed^1]}" + \
                    f" available{when_string}:"
            
            message += "\n" + not_full_title + not_full_update_str

        if full_roles_seperated:
            full_update = []
            for r in full_roles_seperated:
                full_update.append("- " + r.get_notification_role_string())
                
            full_update_str = "\n".join(full_update)
            full_update_str = f"<blockquote>{full_update_str}</blockquote>"

            full_title = f"'{self.title}' has {len(full_roles_seperated)}" + \
                    f" full volunteering role{'s'[:len(full_roles_seperated)^1]}{when_string}:"

            message += "\n" + full_title + full_update_str
        
        message += "\n" + f"Link: <a href={self.url}>{self.url}</a>" + "\n" 
        return message
        

class SignUpRole:
    def __init__(self, title, needed, start_time, end_time, member):
        self.title = title
        self.needed = needed
        self.start_time = start_time
        self.end_time = end_time
        self.member = member #first and last name of student who filled role

    def __str__(self):
        return f"Role title: {self.title} \n Role start time: {get_date_object_without_time(self.get_time_object())} \n Role end time: {get_date_object_without_time(self.get_time_object())} \n Role volunteer: {self.member}"
    

    def from_json(json_object):
        return SignUpRole(
            json_object["title"],
            json_object["needed_count"],
            json_object["start_time"],
            json_object["end_time"],
            json_object["member"] #added for to and from json
        )

    def to_json(self):
        return {
                "title": self.title,
                "needed_count": self.needed,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "member": self.member
            }
    
    def full(self): return self.needed == 0

    def get_testing_role_string(self):
        return f"Title: {self.title}" + "\n" + \
            f"   Status: {self.needed}" + "\n" + \
            f"   Members Joined: {self.member}" + "\n" + \
            f"   Time: {self.start_time} - {self.end_time}"
   
    def get_notification_role_string(self):      
        status_string = f"{self.needed} slot{'s'[:self.needed^1]} available"
        if self.full():
            status_string = f"Full slots"

        notification_string = f"{status_string}"

        if self.start_time != 0:
            days_until = self.get_days_until()
            mdy = self.get_time_object().strftime('%m/%d/%Y')
            if days_until < 1:
                notification_string += f" <b>TODAY</b> ({mdy})"
            elif days_until < 2:
                notification_string += f" <b>TOMORROW</b> ({mdy})"
            else:
                notification_string += f" on <b>{self.get_time_object().strftime('%A')}</b> ({mdy})"
            
            if self.end_time != 0:
                start_time_string = self.get_time_object().strftime("%I:%M %p")
                end_time_string = self.get_end_time_object().strftime("%I:%M %p")
                notification_string += f" from {start_time_string} to {end_time_string}"
                        
        return notification_string
    

    def get_time_object(self):
        return datetime.datetime.fromtimestamp(self.start_time)

    def get_end_time_object(self):
        return datetime.datetime.fromtimestamp(self.end_time)

    def get_hours(self):
        return (self.get_end_time_object() - self.get_time_object()).total_seconds() / 3600

    def has_ended(self):
        return datetime.datetime.now() > self.get_end_time_object()

    def get_hours_until(self):
        return ((self.get_time_object() - datetime.datetime.now()).total_seconds()) / 3600

    def get_days_until(self):
        if self.has_ended():
            return -1
        
        return (get_date_object_without_time(self.get_time_object()) - get_date_object_without_time(datetime.datetime.now())).days


def get_date_object_without_time(date_object):
    return datetime.datetime.strptime(date_object.strftime('%m/%d/%Y'), '%m/%d/%Y')


BASE_SIGNUP_GENIUS_URL = "https://api.signupgenius.com/v2/k"


def fix_signupgenius_url(url):
    if "signupgenius.com" not in url:
        return None

    new_url = url.replace("://m.", "://www.").replace("/#!/showSignUp/", "/go/")
    if not new_url.endswith("#/"): new_url += "#/"
    return new_url

def get_members_to_notify(signups):  #Function with a parameter for an array of signUp objects
    signup_title_array = []  #just the corresponding signup titles for the roles, for reminder messages
    role_array = []  #Array of the roles that corresponds to the signup title array, each includes SignUpRole object
       
    for signup in signups:
        roles = signup.roles  
        for role in roles:
            if role.member != " " and role.get_days_until() == 1:  #If the signUpRole is NOT blank (meaning it hasnt been filled in) and there is 1 day left
                lutil.log(f"{role.member} has {role.get_days_until()} day left before participating in {signup.title}.")
                signup_title_array.append(signup.title)  
                role_array.append(role)
    
    
    
    return role_array, signup_title_array
        



def get_current_signups(signup_genius_token, with_roles=True, log_file_path="latest.txt") -> list[SignUp]:
    signups = []
    

    signups_json, signups_status_code = try_json_request(
        f"{BASE_SIGNUP_GENIUS_URL}/signups/created/active/",
        {"user_key": signup_genius_token},
        log_file_path
    )

    if signups_json != None:
        signups_array = signups_json["data"]
        for signup_json in signups_array:
            signup_id = signup_json["signupid"]
            signup_title = signup_json["title"]
            
            signup_start = signup_json["starttime"]
            signup_end = signup_json["endtime"]

            if signup_start == 0:
                lutil.log(f"'starttime' for '{signup_title}' ({signup_id}) is 0. Setting time to 'startdate'", log_file_path)
                signup_start = signup_json["startdate"]

            if signup_end == 0:
                lutil.log(f"'endtime' for '{signup_title}' ({signup_id}) is 0. Setting time to 'enddate'", log_file_path)
                signup_end = signup_json["enddate"]

            # Sets them to the other time if they're 0, but still allows
            # for the possibility of a "0" or None value for the time.
            # This is just to double check the other time values, since
            # the docs aren't very clear.
            
            signup = SignUp(
                signup_json["signupurl"],
                signup_id,
                signup_title,
                signup_json["contactname"],
                signup_start,
                signup_end
            )
            
            signups.append(signup)

            lutil.log(f"Fetched signup '{signup_title}' with the ID '{signup_id}'", log_file_path)
    else:
        lutil.log(f"Unable to execute signup request. Status Code: {signups_status_code}", log_file_path)

    if with_roles:
        for signup in signups:
            signup_roles = get_signup_roles_available(signup_genius_token, signup.id, log_file_path)
            if signup_roles == None:
                lutil.log("get_signup_roles_available failed, skipping.")
                return None
            else:
                signup.set_roles(signup_roles)

            lutil.log(f"Set roles for signup '{signup.title}'", log_file_path)


    return signups


def server_error(json_resp,status):
    if json_resp == {"message":["Too many report request for the same sign up. Please try again later."],"data":{},"success":False} or status == 500:
        lutil.log(json_resp)
        lutil.log(status)
        return True
    return False


def get_recycling_roles(current_signups):
    recycle_signups = []

    for signup in current_signups:
        if "recycl" in signup.title.lower():
            recycle_signups.append(signup)
    
    recycling_roles = []
    
    for signup in recycle_signups:
        roles = signup.get_roles()
        for role in roles:
            if (get_date_object_without_time(role.get_time_object()) - get_date_object_without_time(datetime.datetime.now() + datetime.timedelta(days=1))).days == 0:
                if role.member != " ":                
                    recycling_roles.append(role)
                    lutil.log(f"Obtained {role.title} bin role from {signup.title}")
    return recycling_roles

        

def get_signup_roles_available(signup_genius_token, signup_id, log_file_path="latest.txt") -> list[SignUpRole]:
    roles = []
    
    params = {
        "user_key": signup_genius_token
    }

    roles_request_url = f"{BASE_SIGNUP_GENIUS_URL}/signups/report/available/{signup_id}/"
    filled_roles_request_url = f"{BASE_SIGNUP_GENIUS_URL}/signups/report/filled/{signup_id}/"

    roles_json, roles_status_code = try_json_request(roles_request_url, params, log_file_path)
    filled_roles_json, filled_roles_status_code = try_json_request(filled_roles_request_url, params, log_file_path)

    if server_error(roles_json,roles_status_code):
        lutil.log("Failed to obtain signup_roles, server error.")
        return None
    roles_to_check = []
    
    if roles_json != None:
        roles_array = roles_json["data"]["signup"]
        for role_json in roles_array: roles_to_check.append(role_json)
    else:
        lutil.log(f"Unable to execute available roles request for signup '{signup_id}'. \
                    Status Code: '{roles_status_code}'", log_file_path)

    
    if filled_roles_json != None:
        filled_roles_array = filled_roles_json["data"]["signup"]
        for filled_role_json in filled_roles_array:
            filled_role_json["myqty"] = 0 # Affirming this is the NEEDED quantity
            roles_to_check.append(filled_role_json)
    else:
        lutil.log(f"Unable to execute filled roles request for signup '{signup_id}'. \
                    Status Code: '{filled_roles_status_code}'", log_file_path)

    for role_json in roles_to_check:
        role_title = role_json["item"]
        role_member = role_json["firstname"] + " " + role_json["lastname"]   #again added to the SignUpRole
        role_start = role_json["startdate"]
        role_end = role_json["enddate"]
        # These assignments are flipped from the assignment
        # under the Signup times, since the pattern at the time of
        # writing has been that the "date" time returns an actual
        # value for the Roles, but not the Signups

        if role_start == 0:
            lutil.log(f"'startdate' for role '{role_title}' under signup {signup_id} is 0. Setting time to 'starttime'", log_file_path)
            role_start = role_json["starttime"]
    
        if role_end == 0:
            lutil.log(f"'enddate' for role '{role_title}' under signup {signup_id} is 0. Setting time to 'endtime'", log_file_path)
            role_end = role_json["endtime"]
        # Again, this still leaves the possibility for a "0" or None
        # value for the time

        roles.append(SignUpRole(
            role_title,
            role_json["myqty"], # Gives the amount of people NEEDED
            role_start,
            role_end, 
            role_member

        ))

        lutil.log(f"Added role '{role_title}' for signup {signup_id} starting on {datetime.datetime.fromtimestamp(role_start).strftime('%m/%d/%Y')}", log_file_path)
    
    return roles


def try_json_request(url, params, log_file_path="latest.txt"):
    current_try = 0
    found_json = None
    status_code = 0

    tries = config_util.get_config_item("request_retries")
    
    while current_try < tries:
        json_request = r.get(url, params)
        status_code = json_request.status_code

        if json_request.ok:
            try:
                found_json = json_request.json()
                lutil.log(f"Successful JSON response for URL: {url} during try {current_try}", log_file_path)
                break
            except json.decoder.JSONDecodeError:
                lutil.log(f"Error fetching JSON response for URL: {url} (failed at try {current_try})", log_file_path)

                if current_try != tries - 1:
                    lutil.log(f"Retrying JSON request for URL: {url}", log_file_path)
                    current_try += 1

                continue
        else:
            break


    return found_json, status_code
        

def get_signups_to_notify(signup_genius_token,
                          days_out=None,
                          days_from=0,
                          hours_out=None,
                          hours_from=0,
                          include_full=True,
                          include_ended=True,
                          log_file_path="latest.txt") -> list[SignUp]:
    if not days_out and not hours_out:
        return None

    signups = []
    for signup in get_current_signups(signup_genius_token, log_file_path=log_file_path):
        roles = signup.get_roles(days_out=days_out,
                                 days_from=days_from,
                                 hours_out=hours_out,
                                 hours_from=hours_from,
                                 include_full=include_full,
                                 include_ended=include_ended)

        if not roles: continue

        signups.append(signup)
        
    return signups


def get_filtered_signups(signups: list[SignUp],
                         days_out=None,
                         days_from=0,
                         hours_out=None,
                         hours_from=0,
                         include_full=True,
                         include_ended=True):
    return list(filter(lambda signup: len(signup.get_roles(days_out=days_out,
                                                       days_from=days_from,
                                                       hours_out=hours_out,
                                                       hours_from=hours_from,
                                                       include_full=include_full,
                                                       include_ended=include_ended)) > 0, signups))
