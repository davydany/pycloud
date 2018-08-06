import os
from pycloud.base import Base
from pycloud.core.provisioners.base import BaseProvisioner
from pycloud.core.keypair_storage import KeyPairStorage
from pycloud.core.registry import Registry
from pycloud.core.provisioners.utils.mixins import AWSProvisionerMixin, FileSystemProvisionerMixin

from sultan.api import Sultan

class SSHKeyGenerator(FileSystemProvisionerMixin, BaseProvisioner):

    name = 'SSH Key Generator'

    slug = 'ssh_keygen'

    description = 'Generates a SSH Key in a temporary directory, and moves it to the requested directory.'

    required_args = ['key_type', 'file', 'passphrase', 'out_dir']

    optional_args = None

    def verify(self, name, key_type=None, file=None, passphrase=None, out_dir=None, **kwargs):

        self.verify_is_not_null('key_type', key_type)
        self.verify_is_not_null('file', file)
        self.verify_is_not_null('passphrase', passphrase)
        self.verify_is_not_null('out_dir', out_dir)

        allowed_key_types = ['dsa', 'ecdsa', 'ed25519', 'rsa', 'rsa1']
        if key_type not in allowed_key_types:
            raise ValueError(
                'SSH Key Generator has a valid key type: %s. Allowed types: %s' % (
                    key_type, 
                    str(allowed_key_types)
                )
            )

    def up(self, name, key_type=None, file=None, passphrase=None, out_dir=None, **kwargs):

        public_keypath = os.path.join(out_dir, 'id_%s.pub' % (key_type))
        private_keypath = os.path.join(out_dir, 'id_%s' % (key_type))

        # make output directory if it doesn't exist
        if not os.path.exists(out_dir):
            self.make_directory(out_dir)

        # don't create a new ssh-key if one already exists, and raise an error.
        if os.path.exists(public_keypath):
            raise IOError("Public Key exists. Halting generation because we don't want to overwrite it.")
        
        if os.path.exists(private_keypath):
            raise IOError("Private Key exists. Halting generation because we don't want to overwrite it.")

        # run ssh-keygen to generate files
        with Sultan.load(cwd=out_dir) as s:
            
            response = s.ssh__keygen(
                '-t', key_type,
                '-f', 'id_%s' % key_type,
            ).run()

            if response.stdout:
                for line in response.stdout:
                    self.logger.debug('STDOUT: %s' % line.strip('\n'))
            
            if response.stderr:
                for line in response.stderr:
                    self.logger.error('STDERR: %s' % line.strip('\n'))

    def down(self, name, key_type=None, file=None, passphrase=None, out_dir=None, **kwargs):


        public_keypath = os.path.join(out_dir, 'id_%s.pub' % (key_type))
        private_keypath = os.path.join(out_dir, 'id_%s' % (key_type))
        self.delete_file(public_keypath)
        self.delete_file(private_keypath)


class UserAdd(AWSProvisionerMixin, FileSystemProvisionerMixin, BaseProvisioner):

    name = 'User Add Provisioner'

    slug = 'user_add'

    description = 'The Linux User Add Provisioner creates a new user on the referenced EC2 Instances.'

    required_args = ['instance_id_ref', 'region', 'key_name', 'user_name',]

    optional_args = ['remote_ssh_port', 'default_shell', 'public_key']

    def verify(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, remote_ssh_port=None, default_shell=None, public_key=None):

        self.verify_is_not_null('instance_id_ref', instance_id_ref)
        self.verify_is_not_null('region', region)
        self.verify_is_not_null('key_name', key_name)
        self.verify_is_not_null('user_name', user_name)

    def fetch_instance_ids(self, instance_id_ref):

        instance_ids = self.config.get(instance_id_ref)
        if not instance_ids:
            raise ValueError("Unable to run user add because there are 0 referenced instances.")
        return instance_ids

    def up(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, remote_ssh_port=22, default_shell=None, public_key=None):

        self.verify_exists(public_key)

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get keypair reference from fs
        fs_keypair = KeyPairStorage(key_name)

        # create the requested user and setup their public SSH Key
        admin_user = 'ubuntu'
        instance_ids = self.fetch_instance_ids(instance_id_ref)
        instances = conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:

            exit_status = self.run_shell_command(conn, instance, fs_keypair, admin_user, remote_ssh_port, 
                'sudo useradd {username} -m -s {default_shell}'.format(
                    username=user_name,
                    default_shell=default_shell
                )
            )
            if exit_status == 0:
                self.logger.info("Successfully added user '%s'" % user_name)
            else:
                self.logger.error("Unable to add user '%s'" % user_name)

            # check if the public key exists
            if public_key:
                self.logger.info("Public Key '%s' was provided. Setting it up for user '%s' on remote instance." % (public_key, user_name))
                public_key_name = os.path.basename(public_key)
                user_ssh_dir = os.path.join('/home', user_name, '.ssh/', public_key_name)
                self.run_shell_command(conn, instance, fs_keypair, admin_user, remote_ssh_port,
                    'sudo mkdir -p {ssh_dir}'.format(ssh_dir=os.path.dirname(user_ssh_dir))
                )
                self.sftp_file(conn, instance, fs_keypair, admin_user, remote_ssh_port, public_key, user_ssh_dir)
                self.run_shell_command(conn, instance, fs_keypair, admin_user, remote_ssh_port,
                    'sudo chmod -R 400 {ssh_dir}'.format(ssh_dir=user_ssh_dir)
                )
        

    def down(self, name, instance_id_ref=None, region=None, key_name=None, user_name=None, AWS_ACCESS_KEY=None, AWS_SECRET_KEY=None, remote_ssh_port=22, default_shell=None, public_key=None):

        # create connection
        conn = self.ec2_connect(region, AWS_ACCESS_KEY, AWS_SECRET_KEY)

        # get keypair reference from fs
        fs_keypair = KeyPairStorage(key_name)

        admin_user = 'ubuntu'
        instance_ids = self.fetch_instance_ids(instance_id_ref)
        instances = conn.get_only_instances(instance_ids=instance_ids)
        for instance in instances:

            exit_status = self.run_shell_command(conn, instance, fs_keypair, admin_user, remote_ssh_port, 
                'sudo userdel {username} -r'.format(
                    username=user_name,
                )
            )

            if exit_status == 0:
                self.logger.info("Successfully deleted user '%s'" % user_name)
            else:
                self.logger.exception("Unable to delete user. Not raising any errors.")
        

Registry.register_provisioner(UserAdd)
Registry.register_provisioner(SSHKeyGenerator)