from pycloud.base import Base
from pycloud.core.provisioners.base import BaseProvisioner
from pycloud.core.keypair_storage import KeyPairStorage
from pycloud.core.registry import Registry
from pycloud.core.provisioners.utils.mixins import AWSProvisionerMixin

class LinuxUserAdd(AWSProvisionerMixin, BaseProvisioner):

    name = 'Linux User Add Provisioner'

    slug = 'linux_user_add'

    description = 'The Linux User Add Provisioner creates a new user on the referenced EC2 Instances.'

    required_args = ['instance_id_ref', 'region', 'key_name', 'user_name']

    optional_args = None

    def verify(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        self.verify_is_not_null('instance_id_ref', instance_id_ref)
        self.verify_is_not_null('region', region)
        self.verify_is_not_null('key_name', key_name)
        self.verify_is_not_null('user_name', user_name)

    def fetch_instance_ids(self, instance_id_ref):

        instance_ids = self.config.get(instance_id_ref)
        if not instance_ids:
            raise ValueError("Unable to run user add because there are 0 referenced instances.")
        return instance_ids

    def up(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get keypair reference from fs
        fs_keypair = KeyPairStorage(key_name)

        admin_user = 'ubuntu'
        instance_ids = self.fetch_instance_ids(instance_id_ref)
        instances = conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            self.run_shell_command(
                conn,
                instance,
                fs_keypair,
                admin_user,
                'useradd %s %s -m -s /bin/bash' % (user_name, user_name)
            )
        



    def down(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None):

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get keypair reference from fs
        fs_keypair = KeyPairStorage(key_name)

        admin_user = 'ubuntu'
        instance_ids = self.fetch_instance_ids(instance_id_ref)
        instances = conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:
            try:
                self.run_shell_command(
                    conn,
                    instance,
                    fs_keypair,
                    admin_user,
                    'userdel %s' % (user_name)
                )
            except Exception:
                self.logger.exception("Unable to delete user. Not raising any errors.")
        

Registry.register_provisioner(LinuxUserAdd)