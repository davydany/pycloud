import os
import yaml
from hashlib import md5 

from pycloud.base import Base
from pycloud.logger import get_logger

logger = get_logger()

class PyCloudConfig(Base):

    DEFAULT_CONFIG_DIR_PATH = os.path.expanduser('~/.pycloud')
    DEFAULT_CONFIG_FILE_PATH = os.path.join(DEFAULT_CONFIG_DIR_PATH, 'config.yml')

    STATE = None
    
    @classmethod
    def initialize_state_mgmt(cls):

        if not os.path.exists(cls.DEFAULT_CONFIG_FILE_PATH):
            if not os.path.exists(cls.DEFAULT_CONFIG_DIR_PATH):
                logger.info("Creating 'pycloud' config directory: %s" % cls.DEFAULT_CONFIG_DIR_PATH)
                os.makedirs(cls.DEFAULT_CONFIG_DIR_PATH)
            with open(cls.DEFAULT_CONFIG_FILE_PATH, 'w') as f:
                logger.info("Creating 'pycloud' config file: %s" % cls.DEFAULT_CONFIG_FILE_PATH)
                f.write('{}')

    # commenting out because hashing with task_name and generating a new key
    # doesn't allow me to share variables between different tasks.
    # ---------------------------
    # def get_hash_key(self, task_name, key):
    #     '''
    #     Generates the hash for 'task_name', and combines the key
    #     for a newly generated key.
    #     '''
    #     m = md5()
    #     m.update(task_name)
    #     return '%s_%s' % (m.hexdigest(), key)


    def flush(self):
        '''
        Writes the contents of PyCloudConfig.STATE to disk.
        '''
        self.logger.debug('Flushing contents to "%s"' % (PyCloudConfig.DEFAULT_CONFIG_FILE_PATH))
        self.logger.debug('Contents: %s' % str(PyCloudConfig.STATE))
        with open(PyCloudConfig.DEFAULT_CONFIG_FILE_PATH, 'w') as outfile:
            yaml.dump(PyCloudConfig.STATE, outfile, default_flow_style=False)

    def get(self, key):
        '''
        Gets the value for the given key.
        '''
        if PyCloudConfig.STATE == None:
            with open(PyCloudConfig.DEFAULT_CONFIG_FILE_PATH) as f:
                try:
                    
                    PyCloudConfig.STATE = yaml.load(f)
                except yaml.YAMLError as err:
                    logger.exception("Unable to load YAML from file '%s'" % PyCloudConfig.DEFAULT_CONFIG_FILE_PATH)
                    PyCloudConfig.STATE = {}
        
        # key = self.get_hash_key(task_name, key)
        return PyCloudConfig.STATE.get(key)

    def set(self, key, value):
        '''
        Sets the value to it's corresponding key.
        '''
        if PyCloudConfig.STATE == None:
            PyCloudConfig.STATE = {}

        # key = self.get_hash_key(task_name, key)
        PyCloudConfig.STATE[key] = value
        self.flush()

    def delete(self, key):
        '''
        Deletes the Key from the Config file
        '''
        if PyCloudConfig.STATE == None:
            return

        # key = self.get_hash_key(task_name, key)
        del PyCloudConfig.STATE[key]
        self.flush()