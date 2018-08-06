import os
from pycloud.base import Base

PYCLOUD_ROOT = os.path.expanduser('~/.pycloud')

class KeyPairStorage(Base):


    KEY_PAIR_DIR = os.path.join(PYCLOUD_ROOT, 'keypairs')

    @classmethod
    def initialize(cls):

        if not os.path.exists(KeyPairStorage.KEY_PAIR_DIR):
            os.makedirs(KeyPairStorage.KEY_PAIR_DIR)

    def __init__(self, key_pair_name):

        self.key_pair_name = key_pair_name
        super(KeyPairStorage, self).__init__()

    @property
    def path_to_pem_dir(self):
        '''
        Path to the directory where the pem files will reside.
        '''
        return KeyPairStorage.KEY_PAIR_DIR

    @property
    def path(self):
        '''
        Path to where the pem file exists for this key pair.
        '''
        return os.path.join(self.path_to_pem_dir, '%s.pem' % (self.key_pair_name))

    @property
    def exists(self):
        '''
        Returns whether or not the pem file corresponding to this key pair exists
        in the file system or not.
        '''
        return os.path.exists(self.path)

    def save(self, keypair):
        '''
        Saves the contents of the boto.ec2.KeyPair class to disk
        '''
        with open(self.path, 'wb') as f:
            f.write(keypair.material.encode('utf-8'))
        os.chmod(self.path, 0o600)

    def delete(self):
        '''
        Deletes the pem file corresponding to this keypair.
        '''
        if self.exists:
            os.remove(self.path)
    
