tasktime
========

*tasktime* reads the information of a project from taskwarrior and calculates, how much time was spent with this project.
*tasktime* can print CSV or readable output.

Usage
-----

    ./tasktime.py [parameters...] <project>

**Parameters**

    -h, --help              Show help message
    -c, --csv               Print output in CSV format
    -n, --null              Print also todos without time information (default: no)
    -t, --task [cmd]        Set task command

Save time with taskwarrior
-------------------------

taskwarrior has the operations *start* and *stop*.
This information is used to calculate the spent time.
You have to start and stop the tasks you work on.

Example:

    task 2 start

    Work on task 2...

    task 2 stop

Examples
--------

**Default output**

    ./tasktime.py cool-project

Output:

    Project: cool-project

    Do something cool
        Duration: 00:13:05
    Do something really cool
        Duration: 02:18:35

    Sum: 02:31:40
    
**Print also tasks without time**
    
    ./tasktime.py -n cool-project

Output:

    Project: cool-project

    Do something cool
        Duration: 00:13:05
    Do something boring
    Do something really cool
        Duration: 02:18:35

    Sum: 02:31:40
