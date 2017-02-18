# Evernote Recurring Tasks & Autoclean Todo Lists

**DISCLAIMER**: This hasn't been tested in a while, so use with caution

## Description

This was an exercise in using the Evernote API with Python.

In Evernote:
- Reminders you want to recur: add "[rec:\<par\>]" at the end, with par being for example: 1d, 3w, 1m, 1y
    - Integer number, followed by
    - d, w, m or y for days, weeks, months or years
    - If the interval is preceeded by a +, as in: [rec:+1w], the recurrence will happen from the done date instead of the due date
- Checklists you want to automatically clean the done items of, tag with *autoclean*

The idea is, you run this script, and changes are applied:
- Completed reminders with the "[rec:\<par\>]" are unchecked and their due date is updated
- Checklists with the autoclean tag: checked items are removed

## Requirements

- The Evernote API for Python
- A Dev Token for either Sandbox account to test or your real account

see the [Evernote API docs](http://dev.evernote.com/doc/start/python.php) for more info

## Files

- config.py and config_sandbox.py: each contain 3 variables
    - DEV_TOKEN: your Evernote API Token
    - sandbox: boolean stating whether or not you're using the sandbox server
    - POLLING_INTERVAL: the script, when run directly, will run every amount of seconds stated in this variables
- app.py: The script itself
    - If you want to use your real account instead of the sandbox account, change the "from config_sandbox import *" line
    - If you don't want it to run infinitely at fixed intervals but use a task scheduler instead: get rid of the while True block at the bottom