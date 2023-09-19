from util import notif_util as nutil
import json


def main():
    config_file = open("config.json")
    data = json.load(config_file)
    token = data["signup_genius_token"]
    testing_canvas = data["testing_canvas_course"]
    config_file.close()

    
    # nutil.send_notification(token,
    #                         days_out=1,
    #                         include_full=False,
    #                         include_when=True)
    # nutil.send_weekly_notification(token)

    
    nutil.send_notification(token,
                            testing_canvas,
                            days_out=2,
                            include_full=False,
                            include_when=True)

    

if __name__ == "__main__":
    main()
