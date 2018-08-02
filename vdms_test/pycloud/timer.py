import click
import datetime
import time
import traceback

class TimeContext(object):

    def __init__(self, name, dry_run=None):

        if dry_run == None:
            dry_run = False

        self.name = name
        self.dry_run = dry_run


    def print_header(self, header):

        click.secho('--| ' + '{:25}'.format(header) + ' |' + '-' * 49, fg='green')

    def print_footer(self, time_taken_sec):

        time_obj = datetime.time(second=int(time_taken_sec))
        click.secho('-' * 50 + ' Time Taken to Execute: {:34}'.format(time_obj.strftime('%H:%M:%S')), fg='green')

    def __enter__(self):

        self.stime = time.time()
        if self.dry_run:
            header = '[DRY-RUN] %s' % self.name
        else:
            header = self.name
        self.print_header(header)

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.etime = time.time()
        if exc_type:
            click.secho("An exception occurred while running.", fg='red')
            click.secho(traceback.format_exc(exc_tb), fg='yellow')

        self.print_footer(self.etime - self.stime)
