import main as m
from util import log_util as lutil, signup_util as su, notif_util as nu
import traceback
import datetime

def main():
    m.daily_job()


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        lutil.log("Exception Thrown:")
        traceback.print_exc()
        
    lutil.handle_logger_close()
    
