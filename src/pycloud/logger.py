import logging
import logging.config as log_config


ALLOWED_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

def configure_logger(level=None):
    '''
    Configures the logger.
    '''
    if level == None:
        level = 'INFO'
    else:
        level = level.upper()

    if level not in ALLOWED_LOG_LEVELS:
        raise ValueError("Invalid Log Level provided: %s; Allowed: %s" % (level, ALLOWED_LOG_LEVELS))

    config = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {
            'level': level,
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s:\t%(message)s'
        },
    },
    'loggers': {
        'pycloud': {
            'handlers': ['stream'],
            'level': level,
            'propagate': False,
        },
        'paramiko': {
            'handlers': ['stream'],
            'level': level,
            'propgate': True
        }
    },
}

    log_config.dictConfig(config)


def get_logger():

    return logging.getLogger('pycloud')
