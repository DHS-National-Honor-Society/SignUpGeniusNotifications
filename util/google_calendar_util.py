from util.signup_util import SignUp
from util import config_util, log_util as lutil
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
import datetime


def get_default_google_calendar():
    return GoogleCalendar(credentials_path="google_credentials.json")


def get_notification_calendar_id():
    return config_util.get_config_item("google_calendar_id")


def get_notification_calendar_events():
    calendar_id = get_notification_calendar_id()

    # Since the get events method is a generator, not returning the array itself,
    # this allows for iteration through it multiple times
    current_events = list(get_default_google_calendar().get_events(calendar_id=calendar_id))

    lutil.log(f"Found {len(current_events)} events under the notification google calendar")
    return current_events

# Returns an object in the following format:
# {
#    "%m-%d-%Y": {
#       "start": [earliest start epoch],
#       "end": [latest end epoch]
#    }
# }
# This is for the purpose of getting the earliest and latest times for each
# individual event, making it so only one event is marked each day instead
# of having duplicates for each role.
# This method will only check signup roles that haven't ended
def get_earliest_role_start_end_times(signup: SignUp):
    role_times_sorted = {}

    for role in signup.get_roles(): # Without filter; all roles

        # Since the calendar checking will only be for later events,
        # checking roles that have already ended isn't necessary
        if role.has_ended():
            lutil.log(f"Role '{role.title}' under signup '{signup.title}' has " + \
                      f"already ended ({timestamp_to_mdy_str(role.end_time)}), not checking for earliest role dates")
            continue
        
        start_date_string = role.get_time_object().strftime("%m/%d/%Y")
        if start_date_string not in role_times_sorted.keys():
            role_times_sorted[start_date_string] = {
                "start": role.start_time,
                "end": role.end_time
            }
            continue

        if role_times_sorted[start_date_string]["start"] > role.start_time:
            role_times_sorted[start_date_string]["start"] = role.start_time

        if role_times_sorted[start_date_string]["end"] < role.end_time:
            role_times_sorted[start_date_string]["end"] = role.end_time

    return role_times_sorted


def timestamp_to_mdy_str(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y")


def add_signups_to_calendar(signups: list[SignUp], current_events: list[Event]=None):
    if not current_events:
        current_events = get_notification_calendar_events()

    for signup in signups:
        add_signup_to_calendar(signup, current_events)
    

def add_signup_to_calendar(signup: SignUp, current_events: list[Event]=None):
    if not current_events:
        current_events = get_notification_calendar_events()

    
    lutil.log(f"Adding signup {signup.title} to the notification google calendar")
    role_times_sorted = get_earliest_role_start_end_times(signup)

    for date_key in role_times_sorted:
        date_times = role_times_sorted[date_key]

        current_role_start_string = timestamp_to_mdy_str(date_times["start"])

        event_already_made = False
        for event in current_events:
            if event.description == None:
                continue
            elif event.start.strftime("%m/%d/%Y") == current_role_start_string and \
                signup.get_url_id() in event.description:
                event_already_made = True
                break


        if not event_already_made:
            lutil.log(f"No event made for '{signup.title}' on {date_key}")
            signup_event = Event(f"{signup.title}",
                                 datetime.datetime.fromtimestamp(date_times["start"]),
                                 datetime.datetime.fromtimestamp(date_times["end"]),
                                 description=signup.url)

            
            get_default_google_calendar().add_event(signup_event,
                                                    calendar_id=get_notification_calendar_id())
            lutil.log(f"Added event for '{signup.title}' on {date_key}")
        else:
            lutil.log(f"Event already made for '{signup.title}' on {date_key}, skipping")

