import click
import datetime
import sys
import time
import traceback

LINE_LIMIT = 120

class TimeContext(object):

    def __init__(self, name, dry_run=None):

        if dry_run == None:
            dry_run = False

        self.name = name
        self.dry_run = dry_run


    def print_header(self, header):

        click.secho('--| ' + '{:25}'.format(header) + ' |' + '-' * (LINE_LIMIT-31), fg='green')

    def sec_to_time(self, sec):

        hrs = sec / 3600
        sec -= 3600*hrs

        mins = sec / 60
        sec -= 60*mins
        return int(hrs), int(mins), int(sec)

    def print_footer(self, time_taken_sec):

        hrs, mins, secs = self.sec_to_time(time_taken_sec)
        time_obj = datetime.time(hour=hrs, minute=mins, second=secs)
        click.secho('-' * (LINE_LIMIT-30) + ' Time Taken to Execute: {:34}'.format(time_obj.strftime('%H:%M:%S')), fg='green')

    def __enter__(self):

        self.stime = time.time()
        if self.dry_run:
            header = '[DRY-RUN] %s' % self.name
        else:
            header = self.name
        self.print_header(header)

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.etime = time.time()
        if exc_tb:
            click.secho("An exception occurred while running.", fg='red')
            for line in traceback.format_tb(exc_tb):
                click.secho(line, fg='yellow')
            click.secho("Halting Execution Now!!", fg='red')
        self.print_footer(self.etime - self.stime)
        if exc_tb:
            click.secho("More Details are printed below:", fg='green')
