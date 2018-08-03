from boto import ec2

import paramiko

from pycloud.base import Base

class AWSProvisionerMixin(Base):

    def run_shell_command(self, connection, instance, fs_keypair, username, command):
        '''
        Runs a command on the provided EC2 Instance as the user.
        '''
        key = paramiko.RSAKey.from_private_key_file(fs_keypair.path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # get details about the instance
        hostname = instance.public_dns_name
        
        # make connection
        self.logger.debug('Establishing Connection "%s@%s"' % (username, hostname))
        stdin, stdout, stderr = client.connect(hostname=hostname, username=username, pkey=key)
        if stdout:
            self.logger.debug("Stdout: %s" % str(stdout.read()))
        if stderr:
            self.logger.error('Stderr: %s' % str(stderr.read()))

        return client.exec_command(command)
     
    def ec2_connect(self, region, aws_access, aws_secret):

        conn = ec2.connect_to_region(
            'us-east-1', 
            aws_access_key_id=aws_access, 
            aws_secret_access_key=aws_secret)
        return conn