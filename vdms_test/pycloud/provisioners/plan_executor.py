import click
import datetime
import time
import traceback
from yaml import load

from vdms_test.base import Base
from vdms_test.pycloud.registry import Registry
from vdms_test.pycloud.errors import InvalidPlanError
from vdms_test.pycloud.timer import TimeContext


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

        self.logger.info("Validating Plan.")
        if not isinstance(self.__plan, list):
            self.logger.error("The plan provided is not a list.")
            raise InvalidPlanError('Plan is not a list')

        for current_plan in self.__plan:
            if len(current_plan) > 1:
                raise InvalidPlanError("Plan's entries must be a dictionary inside a dictionary, of size 1")


    @property
    def provisioners(self):

        try:
            for current_plan in self.__plan:

                provisioner_slug = list(current_plan.keys())[0]
                provisioner_details = current_plan[provisioner_slug]
                print(provisioner_details)

                self.logger.debug("Instantiating Provisioner '%s' with details '%s'" % (
                    provisioner_slug,
                    provisioner_details))

                provisioner_details.update(self.__globals)
                Provisioner = Registry.get(provisioner_slug)
                provisioner = Provisioner()
                provisioner.set_arguments(**provisioner_details)
                yield provisioner
        except ValueError as e:

            raise InvalidPlanError(e)


    def execute_plan(self):
        '''
        Executes the Provisioners requested by the plan with the details
        provided by the Plan.
        '''
        for provisioner in self.provisioners:

            with TimeContext(provisioner.name):
                provisioner.run()


    def dry_execute_plan(self):
        '''
        Simply prints out the plans that are going to be executed.
        '''
        for provisioner in self.provisioners:

            with TimeContext(provisioner.name, dry_run=True):
                time.sleep(1)

    def help(self):
        '''
        Prints out helpful information for each Provisioner.
        '''
        for slug, Provisioner in Registry.content.items():

            Provisioner.help()
