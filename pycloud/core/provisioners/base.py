import click
import os
import py
import textwrap

from pycloud.base import Base
from pycloud.core.config import PyCloudConfig

pycloud_config = PyCloudConfig()

class ImproperlyConfiguredProvisionerError(ValueError):

    pass


class BaseProvisioner(Base):
    '''
    All provisioners must inherit from this base class. 

    It provides argument validation and state storage information.
    '''
    dry_run = False

    name = None

    slug = None

    description = None

    required_args = []

    optional_args = []


    def __init__(self):

        super(BaseProvisioner, self).__init__()
        self.kwargs = None

        # inject the 'task_name' argument to 'required_arguments'
        self.required_args.append('name')

        # verify that Provisioner is configured properly
        if not self.name:
            raise ValueError("Subclass of 'BaseProvisioner' has not defined 'name'.")

        if not self.description:
            raise ValueError("Subclass of 'BaseProvisioner' has not defined 'description'.")

        if not self.slug:
            raise ValueError("Subclass of 'BaseProvisioner' has not defined 'slug'.")

        if (self.required_args != None) and (len(self.required_args) == 0):
            raise ValueError("Subclass of 'BaseProvisioner' needs to have 'required_args' be a list greater than 0, or set to None.")

        if (self.optional_args != None) and (len(self.optional_args) == 0):
            raise ValueError("Subclass of 'BaseProvisioner' needs to have 'optional_args' be a list greater than 0, or set to None.")

    def set_arguments(self, **kwargs):
        '''
        Sets the Provisioner's kwargs.
        '''
        self.kwargs = kwargs
        self.validate_kwargs()

    def verify_is_not_null(self, name, val):

        if val == None:
            raise ValueError('"%s" should not be null' % name)

    def verify_is_type(self, name, val, data_type):

        
        if not isinstance(val, data_type):
            raise ValueError('"%s" is not of type "%s". It is "%s"' % (name, data_type, type(val)))

    def validate_kwargs(self):
        '''
        Validate the kwargs
        '''
        if self.kwargs == None:
            raise ImproperlyConfiguredProvisionerError('Provisioner was not instantiated with arguments. Call set_arguments first.')

        allowed_args = ['PLAN', 'AWS_ACCESS_KEY', 'AWS_SECRET_KEY']
        if self.required_args != None:
            allowed_args += self.required_args

        if self.optional_args != None:
            allowed_args += self.optional_args

        provided_args = self.kwargs.keys()

        # validate required args
        for arg in self.required_args:
            if arg not in self.kwargs:
                raise ImproperlyConfiguredProvisionerError('Required argument "%s" is not found in kwargs.' % arg)

        # ensure that no other args are provided
        for arg in provided_args:
            if arg not in allowed_args:
                raise ImproperlyConfiguredProvisionerError('The configured argument "%s" is not an allowed argument.' % arg)

    def verify(self, **kwargs):
        '''
        This method needs to be implemented and use 'kwargs' for parameters it needs.
        '''
        raise NotImplementedError("Subclass of 'BaseProvisioner' has not implemented 'verify()'.")

    def up(self, name, **kwargs):
        '''
        This method needs to be implemented and use 'kwargs' for parameters it needs.
        '''
        raise NotImplementedError("Subclass of 'BaseProvisioner' has not implemented 'up()'.")

    def down(self, name, **kwargs):
        '''
        This method needs to be implemented and use 'kwargs' for parameters it needs.
        '''
        raise NotImplementedError("Subclass of 'BaseProvisioner' has not implemented 'down()'.")

    def setup(self):

        self.validate_kwargs()
        task_name = self.kwargs.pop('name')
        click.secho("--| SETUP - TASK: %s" % task_name, fg='green')
        self.task_name = task_name
        try:
            self.verify(task_name, **self.kwargs)
        except Exception:
            click.secho("An Error Occurred while trying to verify the inputs in %s.verify()" % (self.__class__.__name__), fg='red')
            raise

        try:
            self.up(task_name, **self.kwargs)
        except Exception:
            click.secho("An Error Occurred while trying to run %s.up()" % (self.__class__.__name__), fg='red')
            raise

    def teardown(self):

        self.validate_kwargs()
        task_name = self.kwargs.pop('name')
        click.secho("--| TEARDOWN - TASK: %s" % task_name, fg='green')
        self.task_name = task_name
        try:
            self.verify(task_name, **self.kwargs)
        except Exception:
            click.secho("An Error Occurred while trying to verify the inputs in %s.verify()" % (self.__class__.__name__), fg='red')
            raise

        try:
            self.down(task_name, **self.kwargs)
        except Exception:
            click.secho("An Error Occurred while trying to run %s.down()" % (self.__class__.__name__), fg='red')
            raise
    # State Management -------------------------------------------------------------------------------------------------
    @property
    def config(self):

        return pycloud_config

    # Help -------------------------------------------------------------------------------------------------------------
    @classmethod
    def help(cls):

        click.secho('-' * 120, fg='green')
        click.secho("Name: %s" % (cls.name), fg='green')
        click.secho("Slug: %s" % (cls.slug), fg='green')
        click.secho("Description:", fg='green')
        for txt in textwrap.wrap(cls.description, 70):
            click.secho("             %s" % txt, fg='green')
        click.secho('Required Arguments:', fg='green')
        if cls.required_args != None:
            for arg in cls.required_args:
                click.secho("                    - %s" % arg, fg='green')
        else:
            click.secho("                    There are 0 required arguments.", fg='green')
        click.secho('Optional Arguments:', fg='green')
        if cls.optional_args != None:
            for arg in cls.optional_args:
                click.secho("                    - %s" % arg, fg='green')
        else:
            click.secho("                    There are 0 optional arguments.", fg='green')
