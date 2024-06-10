#!/usr/bin/env python3

import argparse
import json
import datetime


FILE_NAME = "/home/vigrema/time.json"


def main():
    parser = argparse.ArgumentParser(description="Tracks your very nice work days")
    parser.add_argument("-i", "--check-in", action="store_true", help="Check in")
    parser.add_argument("-o", "--check-out", action="store_true", help="Check out")
    parser.add_argument("-l", "--lunch", action="store_true", help="Lunch start")
    parser.add_argument("-e", "--lunch-end", action="store_true", help="Lunch end")
    parser.add_argument("-s", "--status", action="store_true", help="Show status")
    parser.add_argument("-p", "--pause", action="store_true", help="Start a pause")
    parser.add_argument("-t", "--pause-end", action="store_true", help="End a pause")

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


def check_in():
    if not input("Start new day? (y/n): ") == "y":
        return

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    time_dict = {"in": time_tup}

    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)

    print(f"Checked in at {time.hour}:{time.minute:02}")


def check_out():
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

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

    print(f"You have worked for {int(hours)} hours and {int(minutes)} minutes today.")


def status():
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

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
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    time_dict["lunch_start"] = time_tup

    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)

    print(f"Started lunch at {time.hour}:{time.minute:02}")


def lunch_end():
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    time_dict["lunch_end"] = time_tup

    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)

    print(f"Ended lunch at {time.hour}:{time.minute:02}")
    status()


def pause():
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    if "pauses" not in time_dict:
        time_dict["pauses"] = []
    elif "pause_end" not in time_dict["pauses"][-1]:
        print("There is already an active pause!")
        return

    pause_dict = {"pause_start": time_tup}
    time_dict["pauses"].append(pause_dict)

    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)

    print(f"Paused at {time.hour}:{time.minute:02}")


def pause_end():
    with open(FILE_NAME) as f:
        time_dict = json.load(f)

    time = datetime.datetime.now()
    time_tup = (time.hour, time.minute)
    if "pauses" not in time_dict or "pause_start" not in time_dict["pauses"][-1]:
        print("There is no active pause!")
        return

    time_dict["pauses"][-1]["pause_end"] = time_tup

    with open(FILE_NAME, "w") as f:
        json.dump(time_dict, f)

    print(f"Ended pause at {time.hour}:{time.minute:02}")


if __name__ == "__main__":
    main()
