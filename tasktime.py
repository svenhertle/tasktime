#!/usr/bin/python3

import sys
import subprocess
import json
import re
import datetime

# Calculations
def handle_tasks(tasks):
    seconds = 0
    for t in tasks:
        tmp_seconds = get_task_time(t)
        seconds += tmp_seconds

        print_task(t["description"], tmp_seconds)

    return seconds

def get_task_time(task):
    seconds = 0

    last_start = ""
    if "annotations" in task:
        annotations = task["annotations"]
        for a in annotations:
            if a["description"] == "Started task":
                last_start = a["entry"]
            elif a["description"] == "Stopped task":
                seconds += calc_time_delta(last_start, a["entry"])

    return seconds

def calc_time_delta(start, stop):
    start_time = internal_to_datetime(start)
    stop_time = internal_to_datetime(stop)

    delta = stop_time - start_time

    return delta.total_seconds()

def internal_to_datetime(string):
    match = re.search("^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$", string)

    if match == None:
        return None

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    
    hour = int(match.group(4))
    minute = int(match.group(5))
    second = int(match.group(6))

    return datetime.datetime(year, month, day, hour, minute, second)

# Ouput
def seconds_to_readable(seconds):
    second = seconds % 60
    minute = (seconds // 60) % 60
    hour = (seconds // 3600)

    return number_to_2_digits(hour) + ":" + number_to_2_digits(minute) + ":" + number_to_2_digits(second)

def number_to_2_digits(n):
    return repr(round(n)).zfill(2)

# Prints

def print_header(project):
    print("Project: " + project)
    print()
    print("\"Beschreibung\",\"Dauer\"")

def print_task(description, seconds):
    print("\"" + description.replace("\"", "\"\"") + "\",\"" + seconds_to_readable(seconds) + "\"")

def print_result(seconds):
    print("\"\",\"\"")
    print("\"Sum\",\"" + seconds_to_readable(seconds) + "\"")

def print_help():
    print(sys.argv[0] + " <project>")

# Main
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_help()
        sys.exit(1)

    project = sys.argv[1]

    if project == "help":
        print_help()
    else:
        # Get data from taskwarrior
        try:
            json_tmp = subprocess.check_output(["task", "export", "pro:" + project])
        except subprocess.CalledProcessError as e:
            print("Export from taskwarrior fails: " + str(e.output, encoding="utf8"))
            sys.exit(1)

        # Make valid JSON
        json_str="[" + str(json_tmp, encoding="utf8") + "]"

        # Parse JSON
        tasks = json.loads(json_str)

        # Print data
        print_header(project)
        time = handle_tasks(tasks)
        print_result(time)
