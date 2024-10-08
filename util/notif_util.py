from util import canvas_util as cutil, \
    log_util as lutil, \
    config_util, \
    SMS_util as sms, \
    id_util as ids
from datetime import date, timedelta
import time
def get_notification_message(input_signup_array,
                             days_out=None,
                             days_from=0,
                             hours_out=None,
                             hours_from=0,
                             include_full=True,
                             include_when=False):

    if not days_out and not hours_out:
        return None

    notif_message = ""
    
    for signup in input_signup_array:
        notif_message += signup.get_signup_message(days_out=days_out,
                                                   days_from=days_from,
                                                   hours_out=hours_out,
                                                   hours_from=hours_from,
                                                   include_full=include_full,
                                                   include_time_detail=include_when)

    contacts_string = get_contacts_str("email")

        
    contact_email = "joshua.fernandez@dexterschools.org"
    notif_message += "\n<hr>\n" + "Is there anything incorrect with this " + \
        f"notification? If so, please contact {contacts_string} \n"
    
    notif_message = notif_message.replace("\n", "<br>")

    return notif_message, len(input_signup_array)


def get_contacts_str(type: str) -> str:
    contact_emails = config_util.get_config_item("contacts")

    if type == "email":
        contacts_string = f"{contact_emails[0][0]} (" + \
        f"{contact_emails[0][1]})"
        for i in range(1, len(contact_emails)):
            if len(contact_emails) > 2: contacts_string += ", "

            if(i == len(contact_emails) - 1): contacts_string += "or "

            contacts_string += f"{contact_emails[i][0]} (" + \
                f"<a href='mailto:{contact_emails[i][1]}'>{contact_emails[i][1]}</a>)"

    elif type == "text":
        contacts_string = f"{contact_emails[0][0]} (" + \
        f"{contact_emails[0][1]})"
        for i in range(1, len(contact_emails)):
            if len(contact_emails) > 2: contacts_string += ", "

            if(i == len(contact_emails) - 1): contacts_string += "or "

            contacts_string += f"{contact_emails[i][0]} (" + \
                f"{contact_emails[i][1]})"
        
    return contacts_string


def send_recycle_reminders(recycle_roles):
    is_developer = config_util.get_config_item("developer_mode")

    students = ids.get_student_array()

    for role in recycle_roles:
        role_title = role.title
        recipient = role.member
        contacts = get_contacts_str("text")
        body = f"Have you brought in the {role_title} bin yet? NHS requires you to return your bin before you recieve your hours. Questions? Please reach out to Elijah Smith."
        subject = f"RETURN Recycle Bin"

        if (is_developer):
            lutil.log(cutil.print_reminder(body,subject,recipient,students))
            lutil.log(sms.getPhone(recipient))
        else:
            cutil.send_reminder(body,subject,recipient,students)
            sms.sendSMSreminder(body,recipient)
        time.sleep(1)



def send_reminders(role_array, signup_title_array):  #Function that formats each role and signup title to be sent to canvas
    is_developer = config_util.get_config_item("developer_mode")
    
    students = ids.get_student_array()
    
    for i in range(len(role_array)):  
        role = role_array[i]
        signup_title = signup_title_array[i]
        recipient = role.member
        contacts = get_contacts_str("text")
        start_time_string = role.get_time_object().strftime("%I:%M %p")
        end_time_string = role.get_end_time_object().strftime("%I:%M %p")
        total_time_string = f"from {start_time_string} to {end_time_string}."
        body = f"Dear {recipient}, \n The service you have signed up for, {signup_title} - {role.title} is TOMORROW, {total_time_string}. If there are any conflicts or questions, please reach out to {contacts}"
        subject = f"REMINDER: {signup_title}"
        if (is_developer):
            lutil.log(cutil.print_reminder(body,subject,recipient,students))
            lutil.log(sms.getPhone(recipient))
        else:
            cutil.send_reminder(body,subject,recipient,students)
            sms.sendSMSreminder(body,recipient)
        time.sleep(1)

def send_notification(input_signup_array,
                      canvas_course_id,
                      days_out=None,
                      days_from=0,
                      hours_out=None,
                      hours_from=0,
                      include_full=True,
                      include_when=False,
                      override_title=None):
    if not days_out and not hours_out:
        lutil.log("No ending time given, skipping notification.")
        return

    notif_message, signup_count = get_notification_message(input_signup_array,
                                                           days_out=days_out,
                                                           days_from=days_from,
                                                           hours_out=hours_out,
                                                           hours_from=hours_from,
                                                           include_full=include_full,
                                                           include_when=include_when)

    notif_status = "Daily", f"{days_out} days"
    if hours_out:
        notif_status = "Hourly", f"{hours_out} hours"

    if signup_count == 0:
        lutil.log(f"No signups for {notif_status[0]} Update " + \
                f"({notif_status[1]}), skipping.")
        return

    current_date_str = date.today().strftime("%m/%d/%Y")
    notif_title = f"{override_title if override_title else notif_status[0]}" + \
            f" Update for SignUps ({current_date_str})"
    notif_message = notif_title + "<br>" + notif_message
    cutil.send_announcement(canvas_course_id, notif_title, notif_message)
    
    lutil.log(f"{notif_status[0]} Update ({notif_status[1]}) sent.")


def send_weekly_notification(input_signup_array,
                             canvas_course_id,
                             include_full=True,
                             include_when=False):
    send_notification(input_signup_array,
                      canvas_course_id,
                      days_out=7,
                      include_full=include_full,
                      include_when=include_when,
                      override_title="Weekly")

