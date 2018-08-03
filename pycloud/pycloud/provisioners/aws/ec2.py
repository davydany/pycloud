from boto import ec2

from pycloud.pycloud.provisioners.base import BaseProvisioner
from pycloud.pycloud.registry import Registry

class EC2Provisioner(BaseProvisioner):

    name = 'EC2 Provisioner'

    slug = 'ec2'

    description = 'The EC2 Provisioner can be used to Provision Amazon Web Service\'s EC2 Service'

    required_args = ['region', 'ami_id', 'instance_type', 'security_group',]

    optional_args = ['bar']

    def provision(self, region=None, ami_id=None, instance_type=None, security_group=None,
                  AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        self.verify_is_not_null('region', region)
        self.verify_is_not_null('ami_id', ami_id)
        self.verify_is_not_null('instance_type', instance_type)
        self.verify_is_not_null('security_group', security_group)
        self.verify_is_not_null('AWS_ACCESS_KEY', AWS_ACCESS_KEY)
        self.verify_is_not_null('AWS_SECRET_KEY', AWS_SECRET_KEY)

        connection = ec2.connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)
        connection.run_instances(ami_id, instance=instance_type, security_group=[security_group])




Registry.register_provisioner(EC2Provisioner)
