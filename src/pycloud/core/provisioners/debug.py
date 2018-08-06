import click
import os
import pwd

from pycloud.core.provisioners.base import BaseProvisioner
from pycloud.core.registry import Registry

class DebugProvisioner(BaseProvisioner):

    name = 'Debug Provisioner'

    description = 'A provisioner that prints the contents of "echo", and ' \
                  'if "whoami" is provided, prints the username of the executor.'

    slug = 'debug'

    required_args = ['echo']

    optional_args = ['whoami']

    def up(self, name, echo=None, whoami=None, **kwargs):

        print(echo)

        if whoami:
            uid = os.getuid()
            user = pwd.getpwuid(uid)
            print(user.pw_name)

class ErrorProvisioner(BaseProvisioner):

    name = 'Error Provisioner'

    description = 'A provisioner that always throws an exception. ' \
                  'Useful to see how PyCloud behaves when an exception occurrs.'

    slug = 'err'

    required_args = ['error_msg']

    optional_args = None

    def up(self, name, error_msg, **kwargs):

        click.secho('About to raise exception with message: %s' % error_msg, fg='green')
        raise ValueError(error_msg)


Registry.register_provisioner(DebugProvisioner)
Registry.register_provisioner(ErrorProvisioner)
