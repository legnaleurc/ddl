import datetime
import logging
import logging.handlers


class Logger(object):

    def __init__(self, name, level):
        super().__init__()
        self._logger = logging.getLogger(name)
        self._level = level
        self._parts = []

    def __lshift__(self, part):
        self._parts.append(str(part))
        return self

    def __del__(self):
        msg = ' '.join(self._parts)
        log = getattr(self._logger, self._level)
        log(msg)


def setup_logger(file_path):
    formatter = logging.Formatter('{asctime}|{levelname:_<8}|{message}',
                                  style='{')
    handler = create_handler(file_path, formatter)
    bind_to_logger(handler, (
        'tornado.access',
        'tornado.application',
        'tornado.general',
        'requests.packages.urllib3.connectionpool',
        'acddl',))


def create_handler(path, formatter):
    # alias
    TRFHandler = logging.handlers.TimedRotatingFileHandler
    # rotate on Sunday
    handler = TRFHandler(path, when='w6', atTime=datetime.time())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def bind_to_logger(handler, names):
    for name in names:
        logger = create_logger(name)
        logger.addHandler(handler)


def create_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    return logger


def DEBUG(name):
    return Logger(name, 'debug')


def INFO(name):
    return Logger(name, 'info')


def WARNING(name):
    return Logger(name, 'warning')


def ERROR(name):
    return Logger(name, 'error')


def CRITICAL(name):
    return Logger(name, 'critical')


def EXCEPTION(name):
    return Logger(name, 'exception')
