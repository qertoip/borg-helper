#!/bin/python

import os
import sys
import subprocess
import re
from dateutil import parser
import datetime

# Configure this

days_without_backup_threshold = float(os.environ['DAYS_WITHOUT_BACKUP_THRESHOLD'])
desktop_user_id = int(os.environ['DESKTOP_NOTIFY_USER_ID'])

def exit_backup_server_inaccessible(res):
    title = f'Backup Inaccessible'
    stdout = res.stdout.decode() if res.stdout else ''
    stderr = res.stderr.decode() if res.stderr else ''
    msg = f'{stdout}\n{stderr}'
    desktop_notify(title, msg)
    sys.exit(1)

def exit_no_backup_entries():
    desktop_notify("Backup Missing", "No backup entries found")
    sys.exit(1)

def exit_cant_parse_backup_datetime(backup_entry):
    desktop_notify("Backup Issue", f"Cannot parse backup entry datetime\n\n{backup_entry}")
    sys.exit(1)

def desktop_notify(title, msg, urgency = 'critical'):
    os.system(f"sudo --user='#{desktop_user_id}' DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{desktop_user_id}/bus notify-send '{title}' '{msg}' --urgency={urgency} --expire-time=5")

def last_backup_entry():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    res = subprocess.run([base_dir + '/borg-list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode > 0:
        exit_backup_server_inaccessible(res)
    backup_entries = res.stdout.splitlines()
    if len(backup_entries) == 0:
        exit_no_backup_entries()
    return backup_entries[-1].decode()

def last_backup_datetime():
    s = last_backup_entry();
    res = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', s)
    if res:
        last_backup_datetime_s = res.group(0)
        return parser.parse(last_backup_datetime_s, fuzzy=True)
    else:
        exit_cant_parse_backup_datetime(s)

def days_since_last_backup():
    now = datetime.datetime.now()
    delta = (now - last_backup_datetime())
    return delta.days + delta.seconds / (24*3600)

def main():
    days = days_since_last_backup()
    if (days > days_without_backup_threshold):
        title = f'Backup Missing'
        msg = f'No successful backup over the last {days:.2f} days.\n\ntail /var/log/borg.log'
        desktop_notify(title, msg)

if __name__ == "__main__":
    main()
