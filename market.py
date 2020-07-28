import datetime
import pause

def pause_program(pause_until):
    print("The program is paused until {}".format(pause_until))
    pause.until(pause_until)

def is_open():
    # this function will return true if the market is currently open else false

    remaining_time = 0 # time in seconds until market opens
    date = datetime.datetime.now()
    open_time_date = datetime.datetime(date.year, date.month, date.day, 15, 30) # opens at 3:30pm
    close_time_date = datetime.datetime(date.year, date.month, date.day, 22, 0) # closes at 10pm
    closed_days = ["Saturday", "Sunday"] # days, the stock exchange is closed
    day = date.strftime("%A")

    if day not in closed_days: # if mo-fr
        if date > open_time_date: # if its currently after 15:30
            if date < close_time_date: # if its currently before 22:00
                return True # if market is open
            skip_days = len(closed_days)+1 if day == "Friday" else 1
            pause_program(open_time_date + datetime.timedelta(days=skip_days)) # pause until next open day and its 15:30
        else:
            pause_program(open_time_date) # pause until 15:30 the same day
    else: # only if the program starts at a day in closed_days
        remaining_days = closed_days[::-1].index(day)
        pause_program(open_time_date + datetime.timedelta(days=remaining_days+1)) # pause for remaining_days and 15:30

    return False # if market is closed

if __name__ == "__main__":
    print("\n", market_open(), sep="")
