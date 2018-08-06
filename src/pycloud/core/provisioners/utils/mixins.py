import os
import paramiko
import shutil
import time
import uuid

from boto import ec2
from sultan.api import Sultan

from pycloud.base import Base
from pycloud.core.provisioners.utils.networking import is_port_open

class FileSystemProvisionerMixin(Base):

    # def make_temp_dir(self, suffix=None, prefix='tmp', dir=None):

    #     return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def make_directory(self, path, mode=0o777, exist_ok=False):

        if not os.path.exists(path):
            os.makedirs(path, mode=mode, exist_ok=False)

    def remove_directory(self, path, ignore_errors=False, onerror=None):

        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=ignore_errors, onerror=onerror)

    def copy(self, src, dst, follow_symlinks=True):

        shutil.copy(src, dst, follow_symlinks=follow_symlinks)

    def delete_file(self, path):

        if os.path.exists(path):

            os.remove(path)

class AWSProvisionerMixin(Base):

    def get_paramiko_client(self, connection, instance, fs_keypair, username, ssh_port=22, max_rt=5):
        '''
        Generates a new Paramiko Client from the AWS connection, instance details
        and fs key pair details.
        '''
        key = paramiko.RSAKey.from_private_key_file(fs_keypair.path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # get details about the instance
        hostname = instance.public_dns_name

        # test if default ssh port is accepting connections
        for i in range(max_rt):

            if is_port_open(hostname, int(ssh_port)):
                break
            
            self.logger.info("SSH Port Check %d/%d Times - Port is Not Open. Trying in 10 seconds" % (i+1, max_rt))
            time.sleep(10)
        self.logger.debug("SSH Port Check %d/%d Times - Passed" % (i, max_rt))
        
        # make connection
        client.connect(hostname=hostname, username=username, pkey=key)
        return client

    def sftp_file(self, connection, instance, fs_keypair, username, ssh_port, source, destination, max_rt=5):
        '''
        Transfers an individual file from source to destination using Secure 
        File Transfer Protocol (SFTP).
        '''
        transfer_id = str(uuid.uuid4()).replace('-', '')
        hostname = instance.public_dns_name
        client = self.get_paramiko_client(connection, instance, fs_keypair, username, ssh_port=ssh_port, max_rt=max_rt)
        
        # scp to a temporary place, and then move to final path
        filename = os.path.basename(source)
        temp_destination = os.path.join('/tmp', transfer_id, filename)
        
        # make the parent directory in the remote system
        temp_destination_parent = os.path.dirname(temp_destination)
        self.logger.debug("Making directory: %s" % temp_destination_parent)
        self.run_shell_command(connection, instance, fs_keypair, username, ssh_port, 
            'sudo mkdir -p "%s"' % (temp_destination_parent), 
            max_rt=max_rt)

        self.logger.debug("Changing Ownership of Temporary Directory to %s:%s: %s " % (username, username, temp_destination))
        self.run_shell_command(connection, instance, fs_keypair, username, ssh_port,
            'sudo chown -R %s:%s %s' % (username, username, temp_destination_parent)
        )

        self.logger.info("Starting transfer of '%s' to '%s@%s:%s'" % (source, username, hostname, destination))
        self.logger.debug("Transfering '%s' temporarily to '%s' before moving to '%s'" % (source, temp_destination, destination))
        sftp_client = client.open_sftp()
        sftp_client.put(source, temp_destination)
        sftp_client.close()

        # move the file to the final destination
        self.run_shell_command(connection, instance, fs_keypair, username, ssh_port, 
            'sudo mv "%s" "%s"' % (temp_destination, destination), 
            max_rt=max_rt)

    def run_shell_command(self, connection, instance, fs_keypair, username, ssh_port, command, max_rt=5):
        '''
        Runs a command on the provided EC2 Instance as the user.
        '''
        hostname = instance.public_dns_name
        client = self.get_paramiko_client(connection, instance, fs_keypair, username, ssh_port=ssh_port, max_rt=max_rt)
        self.logger.info("Running Command on %s@%s: %s" % (username, hostname, command))
        result = client.exec_command(command)
        exit_status = -1
        if result:
            stdin, stdout, stderr = result
            exit_status = stdout.channel.recv_exit_status()

            for line in stdout.readlines():
                self.logger.error('STDOUT: %s' % line.strip('\n'))
                self.logger.error('EXIT CODE: %s' % exit_status)

            for line in stderr.readlines():
                self.logger.error('STDERR: %s' % line.strip('\n'))
                self.logger.error('EXIT CODE: %s' % exit_status)

        return exit_status
     
    def ec2_connect(self, region, aws_access, aws_secret):

        conn = ec2.connect_to_region(
            'us-east-1', 
            aws_access_key_id=aws_access, 
            aws_secret_access_key=aws_secret)
        return conn