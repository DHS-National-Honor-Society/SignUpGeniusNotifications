#
#
# {}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
# {}__/\\\\\_____/\\\__/\\\________/\\\_____/\\\\\\\\\\\_________________/\\\\\\\\\\\_______/\\\\\\\\\\\\_            {}
# {} _\/\\\\\\___\/\\\_\/\\\_______\/\\\___/\\\/////////\\\_____________/\\\/////////\\\___/\\\//////////__           {}
# {}  _\/\\\/\\\__\/\\\_\/\\\_______\/\\\__\//\\\______\///_____________\//\\\______\///___/\\\_____________          {}
# {}   _\/\\\//\\\_\/\\\_\/\\\\\\\\\\\\\\\___\////\\\_____________________\////\\\_________\/\\\____/\\\\\\\_         {}
# {}    _\/\\\\//\\\\/\\\_\/\\\/////////\\\______\////\\\_____________________\////\\\______\/\\\___\/////\\\_        {}
# {}     _\/\\\_\//\\\/\\\_\/\\\_______\/\\\_________\////\\\_____________________\////\\\___\/\\\_______\/\\\_       {}
# {}      _\/\\\__\//\\\\\\_\/\\\_______\/\\\__/\\\______\//\\\_____________/\\\______\//\\\__\/\\\_______\/\\\_      {}
# {}       _\/\\\___\//\\\\\_\/\\\_______\/\\\_\///\\\\\\\\\\\/_____________\///\\\\\\\\\\\/___\//\\\\\\\\\\\\/__     {}
# {}        _\///_____\/////__\///________\///____\///////////_________________\///////////______\////////////____    {}
# {}__/\\\\\_____/\\\_______/\\\\\_______/\\\\\\\\\\\\\\\__/\\\\\\\\\\\__/\\\\\\\\\\\\\\\_____/\\\\\\\\\\\___         {}
# {} _\/\\\\\\___\/\\\_____/\\\///\\\____\///////\\\/////__\/////\\\///__\/\\\///////////____/\\\/////////\\\_        {}
# {}  _\/\\\/\\\__\/\\\___/\\\/__\///\\\________\/\\\___________\/\\\_____\/\\\______________\//\\\______\///__       {}
# {}   _\/\\\//\\\_\/\\\__/\\\______\//\\\_______\/\\\___________\/\\\_____\/\\\\\\\\\\\_______\////\\\_________      {}
# {}    _\/\\\\//\\\\/\\\_\/\\\_______\/\\\_______\/\\\___________\/\\\_____\/\\\///////___________\////\\\______     {}
# {}     _\/\\\_\//\\\/\\\_\//\\\______/\\\________\/\\\___________\/\\\_____\/\\\_____________________\////\\\___    {}
# {}      _\/\\\__\//\\\\\\__\///\\\__/\\\__________\/\\\___________\/\\\_____\/\\\______________/\\\______\//\\\__   {}
# {}       _\/\\\___\//\\\\\____\///\\\\\/___________\/\\\________/\\\\\\\\\\\_\/\\\_____________\///\\\\\\\\\\\/___  {}
# {}        _\///_____\/////_______\/////_____________\///________\///////////__\///________________\///////////_____ {}
# {}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}
#
# Contributors:
# Josh Fernandez, Class of 2024
# Carson Chan, Class of 2025
# Oliver Pham, Class of 2025
# Arman Buyukbozkirli, Class of 2026
#


from util import notif_util as nutil, \
    log_util as lutil, canvas_util as cutil, \
    config_util, signup_util as sutil, \
    google_calendar_util as gcutil
import schedule
import time
import traceback
import json
import datetime

current_signups = []


def hourly_job():
    lutil.log("Starting hourly job...")
    
    conf = config_util.get_config()
    
    current_signups = sutil.get_current_signups(conf["signup_genius_token"])
    job_signups = sutil.get_filtered_signups(current_signups,
                                             hours_out=2,
                                             hours_from=1,
                                             include_full=False,
                                             include_ended=False)
    
    nutil.send_notification(job_signups,
                            conf["default_canvas_course"],
                            hours_out=2,
                            hours_from=1,
                            include_full=False,
                            include_when=True)

    gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Hourly job done.")


def daily_job():
    lutil.log("Starting daily job...")
    
    conf = config_util.get_config()
    now = datetime.datetime.now()

    if now.strftime("%A") == conf["weekly_update_day"]:
        lutil.log("Moving to weekly job...")
        weekly_job()
        return

    
    current_signups = sutil.get_filtered_signups(sutil.get_current_signups(conf["signup_genius_token"]),include_ended=False,include_full=True)
    
    members,signup_titles = sutil.get_members_to_notify(current_signups)
    
    nutil.send_reminders(members, signup_titles)  
    
    job_signups = sutil.get_filtered_signups(current_signups,
                                             days_out=1,
                                             include_full=False,
                                             include_ended=False)
    

    # nutil.send_notification(job_signups,
    #                         conf["default_canvas_course"],
    #                         days_out=1,
    #                         include_full=False,
    #                         include_when=True)

    # gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Daily job done.")
    

def weekly_job():
    lutil.log("Starting weekly job...")
    
    conf = config_util.get_config()

    current_signups = sutil.get_current_signups(conf["signup_genius_token"])
    job_signups = sutil.get_filtered_signups(current_signups,
                                             days_out=7,
                                             include_full=False,
                                             include_ended=False)
    
    nutil.send_weekly_notification(job_signups,
                                   conf["default_canvas_course"],
                                   include_full=False,
                                   include_when=False) # No need to say "in the next 7 days"

    gcutil.add_signups_to_calendar(current_signups)

    lutil.log("Weekly job done.")

    

def main():
    lutil.log("Starting script...")

    daily_time = config_util.get_config_item("daily_time")
    hourly_minute = config_util.get_config_item("hourly_minute")

    # schedule.every().hour.at(hourly_minute).do(hourly_job)

    schedule.every().day.at(daily_time).do(daily_job)

    while True:
        schedule.run_pending()
        time.sleep(60)
  

if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        lutil.log("Exception Thrown:")
        traceback.print_exc()
        
    lutil.handle_logger_close()


    
