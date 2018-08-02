import click
import os
import pwd

from vdms_test.pycloud.provisioners.base import BaseProvisioner
from vdms_test.pycloud.registry import Registry

class DebugProvisioner(BaseProvisioner):

    name = 'Debug Provisioner'

    description = 'A provisioner that prints the contents of "echo", and ' \
                  'if "whoami" is provided, prints the username of the executor.'

    slug = 'debug'

    required_args = ['echo']

    optional_args = ['whoami']

    def provision(self, echo=None, whoami=None, **kwargs):

        print(echo)

        if whoami:
            uid = os.getuid()
            user = pwd.getpwuid(uid)
            print(user.pw_name)

class ErrorProvisioner(BaseProvisioner):

    name = 'Error Provisioner'

    description = 'A provisioner that always throws an exception. ' \
                  'Useful to see how PyCloud behaves when an exception occurrs.'

    required_args = ['error_msg']

    optional_args = None

    def provision(self, error_msg, **kwargs):

        click.secho('About to raise exception with message: %s' % error_msg, fg='green')
        raise ValueError(error_msg)


Registry.register_provisioner(DebugProvisioner)
Registry.register_provisioner(ErrorProvisioner)
