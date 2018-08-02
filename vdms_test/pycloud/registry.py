from vdms_test.logger import get_logger

from vdms_test.base import Base

logger = get_logger()

class RegistryManager(Base):

    def __init__(self):

        super(RegistryManager, self).__init__()
        self.__registry = {}

    def register_provisioner(self, provisioner_klass):
        '''
        Registers a Provisioner Class 'provisioner_klass', with slug 'provisioner_slug'.
        '''
        provisioner_slug = provisioner_klass.slug
        if provisioner_slug not in self.__registry:
            self.__registry[provisioner_slug] = provisioner_klass

        else:
            raise ValueError("Provisioner with slug '%s' has already been registered." % (provisioner_slug))

    def get(self, provisioner_slug):
        '''
        Returns the Provisioner Class registered with slug 'provisioner_slug'.
        '''
        if provisioner_slug in self.__registry:
            return self.__registry[provisioner_slug]

        raise ValueError("Provisioner linked with slug '%s' has not been registered." % (provisioner_slug))

    @property
    def content(self):
        '''
        Returns the contents of the Registry.
        '''
        return self.__registry

Registry = RegistryManager()


from .provisioners import *

logger.info("There are %d Provisioners Registered." % len(Registry.content))
