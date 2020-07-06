import logging
import os
from logging.config import dictConfig

from demo_iot_connect.config import settings

DEFAULT_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def verbose_formatter(verbose: bool) -> str:
    if verbose is True:
        return 'verbose'
    else:
        return 'simple'


def log_level(debug: bool, level: str) -> str:
    if debug is True:
        level_num = logging.DEBUG
    else:
        level_num = logging.getLevelName(level)
    settings.set('LOGLEVEL', logging.getLevelName(level_num))
    return settings.LOGLEVEL


# 合并 Log 级别
LOG_LEVEL = log_level(settings.DEBUG, settings.LOGLEVEL)

# 如果日志目录不存在，就新建
os.makedirs(settings.LOGPATH, exist_ok=True)

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "console": {
            "formatter": verbose_formatter(settings.VERBOSE),
            'level': 'DEBUG',
            "class": "logging.StreamHandler",
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': verbose_formatter(settings.VERBOSE),
            'filename': os.path.join(settings.LOGPATH, 'socket_server.log'),
            'maxBytes': 1024 * 1024 * 1024 * 200,  # 200M
            'backupCount': '5',
            'encoding': 'utf-8'
        },
        'access_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'access',
            'filename': os.path.join(settings.LOGPATH, 'access.log'),
            'maxBytes': 1024 * 1024 * 1024 * 200,  # 200M
            'backupCount': '5',
            'encoding': 'utf-8'
        }
    },
    "loggers": {
        '': {'level': LOG_LEVEL, 'handlers': ['console', 'file']},
        'uvicorn.access': {'handlers': ['access_file', 'console'], 'level': LOG_LEVEL, 'propagate': False},
    }
}


def configure_logging():
    dictConfig(DEFAULT_LOGGING)
