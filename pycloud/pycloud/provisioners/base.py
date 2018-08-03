import click
import textwrap

from pycloud.base import Base

class ImproperlyConfiguredProvisionerError(ValueError):

    pass


class BaseProvisioner(Base):

    name = None

    slug = None

    description = None

    required_args = []

    optional_args = []

    def __init__(self):

        super(BaseProvisioner, self).__init__()
        self.kwargs = None

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


    def provision(self, **kwargs):
        '''
        This method needs to be implemented and use 'self.kwargs'.
        '''
        raise NotImplementedError("Subclass of 'BaseProvisioner' has not implemented 'provision()'.")

    def run(self):

        self.validate_kwargs()
        self.provision(**self.kwargs)


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
