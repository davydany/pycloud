import click
import datetime
import time
import traceback
from yaml import load

from pycloud.base import Base
from pycloud.core.registry import Registry
from pycloud.core.errors import InvalidPlanError
from pycloud.core.timer import TimeContext


class PlanExecutor(Base):
    '''
    Uses Provisioners to execute the given plan.
    '''
    def __init__(self, plan_path, _globals=None):

        super(PlanExecutor, self).__init__()
        self.__globals = _globals if _globals != None else {}

        if plan_path != None:
            with open(plan_path) as f:
                self.__plan = load(f.read())
            self.validate_plan()
        else:
            self.__plan = []

    def validate_plan(self):

        required_keys = ['tasks']

        self.logger.debug("Validating Plan.")
        for key in required_keys:
            if key not in self.__plan:
                raise InvalidPlanError("Plan does not have a set of 'tasks'")
                
        if not isinstance(self.__plan['tasks'], list):
            self.logger.error("The plan provided is not a list.")
            raise InvalidPlanError('Plan is not a list')


        for current_task in self.__plan['tasks']:
            if len(current_task) > 1:
                raise InvalidPlanError("Plan's entries must be a dictionary inside a dictionary, of size 1")



    @property
    def setup_provisioners(self):

        try:
            for current_task in self.__plan['tasks']:

                provisioner_slug = list(current_task.keys())[0]
                task_details = current_task[provisioner_slug]

                self.logger.debug("Instantiating Provisioner '%s' with details '%s'" % (
                    provisioner_slug,
                    task_details))

                task_details.update(self.__globals)
                Provisioner = Registry.get(provisioner_slug)
                provisioner = Provisioner()
                provisioner.set_arguments(**task_details)
                yield provisioner
        except ValueError as e:
            click.secho("ERROR: %s" % e, fg='red')
            raise InvalidPlanError(e)

    @property
    def teardown_provisioners(self):

        try:
            for current_task in self.__plan['tasks'][::-1]:

                provisioner_slug = list(current_task.keys())[0]
                task_details = current_task[provisioner_slug]

                self.logger.debug("Instantiating Provisioner '%s' with details '%s'" % (
                    provisioner_slug,
                    task_details))

                task_details.update(self.__globals)
                Provisioner = Registry.get(provisioner_slug)
                provisioner = Provisioner()
                provisioner.set_arguments(**task_details)
                yield provisioner
        except ValueError as e:
            click.secho("ERROR: %s" % e, fg='red')
            raise InvalidPlanError(e)


    def setup(self):
        '''
        Executes the Provisioners requested by the plan with the details
        provided by the Plan.
        '''
        for provisioner in self.setup_provisioners:

            with TimeContext(provisioner.name):
                provisioner.dry_run = False
                provisioner.setup()


    def dry_setup(self):
        '''
        Simply prints out the plans that are going to be executed.
        '''
        for provisioner in self.setup_provisioners:

            with TimeContext(provisioner.name, dry_run=True):
                provisioner.dry_run = True
                provisioner.setup()

    def teardown(self):
        '''
        Executes the Provisioners requested by the plan in erverse order with
        the details provided by the Plan.
        '''
        for provisioner in self.teardown_provisioners:

            with TimeContext(provisioner.name):
                provisioner.dry_run = False
                provisioner.teardown()

    def dry_teardown(self):
        '''
        Executes the Provisioners requested by the plan in erverse order with
        the details provided by the Plan.
        '''
        for provisioner in self.teardown_provisioners:

            with TimeContext(provisioner.name):
                provisioner.dry_run = True
                provisioner.teardown()

    def help(self):
        '''
        Prints out helpful information for each Provisioner.
        '''
        for slug, Provisioner in Registry.content.items():

            Provisioner.help()
