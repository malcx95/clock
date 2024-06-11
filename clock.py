#!/usr/bin/env python3

import argparse
import json
import datetime
from pathlib import Path


FILE_NAME = Path.home() / ".clock.json"


def main():
    parser = argparse.ArgumentParser(description="Tracks your very nice work days")
    parser.add_argument("-i", "--check-in", action="store_true", help="Check in")
    parser.add_argument("-o", "--check-out", action="store_true", help="Check out")
    parser.add_argument("-l", "--lunch", action="store_true", help="Lunch start")
    parser.add_argument("-e", "--lunch-end", action="store_true", help="Lunch end")
    parser.add_argument("-s", "--status", action="store_true", help="Show status")
    parser.add_argument("-p", "--pause", action="store_true", help="Start a pause")
    parser.add_argument("-t", "--pause-end", action="store_true", help="End a pause")
    parser.add_argument("-m", "--month-summary", action="store_true", help="Show summary of the current month")

    args = parser.parse_args()

    if args.check_in:
        check_in()
    elif args.lunch:
        lunch_start()
    elif args.lunch_end:
        lunch_end()
    elif args.check_out:
        check_out()
    elif args.status:
        status()
    elif args.pause:
        pause()
    elif args.pause_end:
        pause_end()
    elif args.month_summary:
        month_summary()


def month_summary():
    days_of_the_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
    time_dict = load_time_dict()

    now = datetime.datetime.now()
    year = now.year
    month = now.month

    year_month = str(year) + str(month)

    if year_month not in time_dict:
        print("No data for this month.")
        return

    this_month = time_dict[year_month]

    for day in this_month:
        weekday_number = datetime.date(year=year, month=month, day=int(day)).weekday()
        weekday = days_of_the_week[weekday_number]

        if "diff" not in this_month[day]:
            continue

        negative = False
        diff_seconds = this_month[day]["diff"]
        total_working_seconds = datetime.timedelta(hours=8).total_seconds() + diff_seconds

        if diff_seconds < 0:
            diff_seconds = -diff_seconds
            negative = True

        diff_hours = int(diff_seconds // 3600)
        diff_minutes = int((diff_seconds - diff_hours * 3600) // 60)

        total_working_hours = int(total_working_seconds // 3600)
        total_working_minutes = int((total_working_seconds - total_working_hours * 3600) // 60)

        print(f"{year}-{month:02}-{int(day):02} {weekday}:\t {total_working_hours}:{total_working_minutes:02} \t (Difference to 8 hours: {'-' if negative else '+'}{diff_hours}:{diff_minutes:02})")
        if weekday_number == 4:
            print()

    negative, diff_hours, diff_minutes = get_this_months_total_diff(time_dict)
    print(f"This month's total difference to 8 hours/day is {'-' if negative else '+'}{int(diff_hours)}:{int(diff_minutes):02}.")


def update_todays_time(time_dict, key, time_tup):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = str(now.day)

    year_month = str(year) + str(month)

    if year_month not in time_dict:
        time_dict[year_month] = {}

    this_month = time_dict[year_month]

    if day not in this_month:
        this_month[day] = {}

    this_day = this_month[day]
    this_day[key] = time_tup

    return time_dict


def save_time_dict(time_dict):
    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)


def get_todays_time(time_dict):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = str(now.day)

    year_month = str(year) + str(month)

    if year_month not in time_dict:
        return None

    this_month = time_dict[year_month]

    if day not in this_month:
        return None

    return this_month[day]


def load_time_dict():
    try:
        with open(FILE_NAME) as f:
            time_dict = json.load(f)
    except FileNotFoundError:
        time_dict = {}

    return time_dict


def check_in():
    if not input("Start new day? (y/n): ") == "y":
        return

    time_dict = load_time_dict()

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)

    updated_time_dict = update_todays_time(time_dict, "in", time_tup)

    save_time_dict(updated_time_dict)

    print(f"Checked in at {time.hour}:{time.minute:02}")


def check_out():
    total_time_dict = load_time_dict()

    time_dict = get_todays_time(total_time_dict)

    time = datetime.datetime.now()

    check_in_hour, check_in_minute = time_dict["in"]
    lunch_start_hour, lunch_start_minute = time_dict["lunch_start"]
    lunch_end_hour, lunch_end_minute = time_dict["lunch_end"]

    check_in_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=check_in_hour, minute=check_in_minute)
    check_out_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=time.hour, minute=time.minute)

    lunch_start_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=lunch_start_hour, minute=lunch_start_minute)
    lunch_end_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=lunch_end_hour, minute=lunch_end_minute)

    total_time = (check_out_time - check_in_time) - (lunch_end_time - lunch_start_time)
    if "pauses" in time_dict:
        for pause_dict in time_dict["pauses"]:
            pause_start_hour, pause_start_minute = pause_dict["pause_start"]
            pause_end_hour, pause_end_minute = pause_dict["pause_end"]

            pause_start_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=pause_start_hour, minute=pause_start_minute)
            pause_end_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=pause_end_hour, minute=pause_end_minute)

            total_time -= pause_end_time - pause_start_time

    total_seconds = total_time.total_seconds()

    hours = total_seconds // 3600
    minutes = (total_seconds - hours * 3600) // 60

    difference_to_8_hours = total_time - datetime.timedelta(hours=8)
    total_time_dict = update_todays_time(total_time_dict, "diff", difference_to_8_hours.total_seconds())
    negative = False

    if (difference_to_8_hours.total_seconds() < 0):
        difference_to_8_hours = -difference_to_8_hours
        negative = True

    diff_hours = difference_to_8_hours.total_seconds() // 3600
    diff_minutes = (difference_to_8_hours.total_seconds() - diff_hours * 3600) // 60

    total_time_dict = update_todays_time(total_time_dict, "out", (time.hour, time.minute))

    total_negative, total_diff_hours, total_diff_minutes = get_this_months_total_diff(total_time_dict)

    save_time_dict(total_time_dict)

    print(f"You have worked for {int(hours)} hours and {int(minutes)} minutes today.\n")
    print(f"Today's difference to 8 hours is {'-' if negative else '+'}{int(diff_hours)}:{int(diff_minutes):02}.\n")
    print(f"This month's total difference to 8 hours/day is {'-' if negative else '+'}{int(total_diff_hours)}:{int(total_diff_minutes):02}.\n")


def get_this_months_total_diff(time_dict):
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    year_month = str(year) + str(month)

    if year_month not in time_dict:
        return 0

    this_month = time_dict[year_month]

    total_diff = datetime.timedelta(0)

    for day in this_month:
        if "diff" in this_month[day]:
            diff_seconds = this_month[day]["diff"]
            total_diff += datetime.timedelta(seconds=diff_seconds)

    negative = False
    if total_diff.total_seconds() < 0:
        total_diff = -total_diff
        negative = True

    diff_hours = total_diff.total_seconds() // 3600
    diff_minutes = (total_diff.total_seconds() - diff_hours * 3600) // 60
    return negative, int(diff_hours), int(diff_minutes)


def status():
    total_time_dict = load_time_dict()
    time_dict = get_todays_time(total_time_dict)

    time = datetime.datetime.now()

    check_in_hour, check_in_minute = time_dict["in"]
    if "lunch_end" in time_dict:
        lunch_start_hour, lunch_start_minute = time_dict["lunch_start"]
        lunch_end_hour, lunch_end_minute = time_dict["lunch_end"]

        check_in_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=check_in_hour, minute=check_in_minute)
        check_out_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=time.hour, minute=time.minute)

        lunch_start_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=lunch_start_hour, minute=lunch_start_minute)
        lunch_end_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=lunch_end_hour, minute=lunch_end_minute)

        total_time = (check_out_time - check_in_time) - (lunch_end_time - lunch_start_time)
        if "pauses" in time_dict:
            for pause_dict in time_dict["pauses"]:
                pause_start_hour, pause_start_minute = pause_dict["pause_start"]
                pause_end_hour, pause_end_minute = pause_dict["pause_end"]

                pause_start_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=pause_start_hour, minute=pause_start_minute)
                pause_end_time = datetime.datetime(year=time.year, month=time.month, day=time.day, hour=pause_end_hour, minute=pause_end_minute)

                total_time -= pause_end_time - pause_start_time

        total_seconds = total_time.total_seconds()

        hours = total_seconds // 3600
        minutes = (total_seconds - hours * 3600) // 60

        eight_hour_delta = datetime.timedelta(hours=8)
        time_to_eight_hours = eight_hour_delta - total_time

        time_at_eight_hours = time + time_to_eight_hours

        print(f"You have worked for {int(hours)} hours and {int(minutes)} minutes today.")
        print(f"You had lunch at {lunch_start_hour}:{lunch_start_minute:02}-{lunch_end_hour}:{lunch_end_minute:02}")
        print(f"You will reach 8 hours at {time_at_eight_hours.hour}:{time_at_eight_hours.minute:02}")
    else:
        print(f"You checked in at {check_in_hour}:{check_in_minute:02}")


def lunch_start():
    total_time_dict = load_time_dict()
    time_dict = get_todays_time(total_time_dict)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    time_dict["lunch_start"] = time_tup

    save_time_dict(total_time_dict)

    print(f"Started lunch at {time.hour}:{time.minute:02}")


def lunch_end():
    total_time_dict = load_time_dict()
    time_dict = get_todays_time(total_time_dict)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    time_dict["lunch_end"] = time_tup

    save_time_dict(total_time_dict)

    print(f"Ended lunch at {time.hour}:{time.minute:02}")
    status()


def pause():
    total_time_dict = load_time_dict()
    time_dict = get_todays_time(total_time_dict)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    if "pauses" not in time_dict:
        time_dict["pauses"] = []
    elif "pause_end" not in time_dict["pauses"][-1]:
        print("There is already an active pause!")
        return

    pause_dict = {"pause_start": time_tup}
    time_dict["pauses"].append(pause_dict)

    save_time_dict(total_time_dict)

    print(f"Paused at {time.hour}:{time.minute:02}")


def pause_end():
    time_dict = load_time_dict()

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    if "pauses" not in time_dict or "pause_start" not in time_dict["pauses"][-1]:
        print("There is no active pause!")
        return

    time_dict["pauses"][-1]["pause_end"] = time_tup

    save_time_dict(time_dict)

    print(f"Ended pause at {time.hour}:{time.minute:02}")


if __name__ == "__main__":
    main()
