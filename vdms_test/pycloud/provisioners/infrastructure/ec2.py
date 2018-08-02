from vdms_test.pycloud.provisioners.base import BaseProvisioner
from vdms_test.pycloud.registry import Registry

class EC2Provisioner(BaseProvisioner):

    name = 'EC2 Provisioner'

    slug = 'ec2'

    description = 'The EC2 Provisioner can be used to Provision Amazon Web Service\'s EC2 Service'

    required_args = ['foo']

    optional_args = ['bar']

    def provision(self, foo=None, bar=None):

        print('Provisioning ...')


Registry.register_provisioner(EC2Provisioner)
