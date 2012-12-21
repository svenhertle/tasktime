#!/usr/bin/python3

import sys
import subprocess
import json
import re
import datetime

#
# Calculations
#

class Calculator:
    printer = None

    task_cmd = "task"

    print_null = False

    def __init__(self):
        self.printer = ReadablePrinter()

    def setPrinter(self, printer):
        self.printer = printer

    def setTaskCmd(self, task_cmd):
        self.task_cmd = task_cmd
    
    def setPrintNull(self, print_null):
        self.print_null = print_null

    def create_statistic(self, project):
        if self.printer == None:
            print("Printer is None")
            sys.exit(1)

        # Get data from taskwarrior
        try:
            json_tmp = subprocess.check_output([self.task_cmd, "export", "pro:" + project])
        except OSError as e:
            print(str(e))
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print("Export from taskwarrior fails: " + str(e.output, encoding="utf8"))
            sys.exit(1)

        # Make valid JSON
        json_str="[" + str(json_tmp, encoding="utf8") + "]"

        # Parse JSON
        tasks = json.loads(json_str)

        # Print data
        self.printer.print_header(project)
        time = self.handle_tasks(tasks)
        self.printer.print_result(time)

    def handle_tasks(self, tasks):
        seconds = 0
        for t in tasks:
            tmp_seconds = self.get_task_time(t)
            seconds += tmp_seconds

            if self.print_null or tmp_seconds != 0:
                self.printer.print_task(t["description"], tmp_seconds)

        return seconds

    def get_task_time(self, task):
        seconds = 0

        last_start = ""
        if "annotations" in task:
            annotations = task["annotations"]
            for a in annotations:
                if a["description"] == "Started task":
                    last_start = a["entry"]
                elif a["description"] == "Stopped task":
                    seconds += self.calc_time_delta(last_start, a["entry"])

        return seconds

    def calc_time_delta(self, start, stop):
        start_time = self.internal_to_datetime(start)
        stop_time = self.internal_to_datetime(stop)

        delta = stop_time - start_time

        return delta.total_seconds()

    def internal_to_datetime(self, string):
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

#
# Printer
#

class Printer:
    def print_header(self, project):
        raise NotImplementedError()
    
    def print_task(self, description, seconds):
        raise NotImplementedError()
    
    def print_result(self, seconds):
        raise NotImplementedError()

    def seconds_to_readable(self, seconds):
        second = seconds % 60
        minute = (seconds // 60) % 60
        hour = (seconds // 3600)

        return self._number_to_2_digits(hour) + ":" + self._number_to_2_digits(minute) + ":" + self._number_to_2_digits(second)

    def _number_to_2_digits(self, n):
        return repr(round(n)).zfill(2)

# CSV
class CSVPrinter(Printer):
    def _csv_encode(self, string):
        return string.replace("\"", "\"\"")

    def print_header(self, project):
        print("\"Project\",\"" + self._csv_encode(project) + "\"")
        print("\"\",\"\"")
        print("\"Description\",\"Duration (hours)\"")
        print("\"\",\"\"")

    def print_task(self, description, seconds):
        print("\"" + self._csv_encode(description) + "\",\"" + self.seconds_to_readable(seconds) + "\"")

    def print_result(self, seconds):
        print("\"\",\"\"")
        print("\"Sum\",\"" + self.seconds_to_readable(seconds) + "\"")

# Readable
class ReadablePrinter(Printer):
    def print_header(self, project):
        print("Project: " + project)
        print()

    def print_task(self, description, seconds):
        print(description)
        if seconds != 0:
            print("\tDuration: " + self.seconds_to_readable(seconds))

    def print_result(self, seconds):
        print()
        print("Sum: " + self.seconds_to_readable(seconds))

# Help
def print_help():
    print(sys.argv[0] + " [parameters...] <project>")
    print()
    print("Calculate and print time for a project from taskwarrior")
    print()
    print("Parameters:")
    print("\t-h, --help\t\tShow this help")
    print("\t-c, --csv\t\tPrint output in CSV format")
    print("\t-n, --null\t\tPrint also todos without time information (default: no)")
    print("\t-t, --task [cmd]\tSet task command")

#
# Main
#

if __name__ == "__main__":
    params = sys.argv[1:]
    
    c = Calculator()

    project = None
    show_help = False

    skip = False
    for i,param in enumerate(params):
        if skip:
            skip = False
            continue

        if param == "--csv" or param == "-c":
            c.setPrinter(CSVPrinter())
        elif param == "--help" or param == "-h":
            show_help = True
        elif param == "--task" or param == "-t":
            if i == len(params)-1: # Last parameter -> error
                print("--task needs another parameter")
                sys.exit(1)
            else:
                c.setTaskCmd(params[i+1])
                skip = True
        elif param == "--null" or param == "-n":
            c.setPrintNull(True)
        elif i == len(params)-1: # Last parameter
            project = param

    if show_help or project == None:
        print_help()
    else:
        c.create_statistic(project)
