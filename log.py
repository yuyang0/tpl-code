#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""

"""
import os
import logging


LOG_DIR = "/your/dir"


class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.INFO, logging.WARNING)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detail": {
            "format": "%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)15s() ]: %(levelname)-8s %(message)s"
        }
    },
    "filters": {
        "debug_filter": {
            '()': DebugFilter,
        },
        "info_filter": {
            '()': InfoFilter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detail",
            "stream": "ext://sys.stdout"
        },
        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filters": ["debug_filter", ],
            "formatter": "detail",
            "filename": os.path.join(LOG_DIR, "logs/debug.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filters": ["info_filter", ],
            "formatter": "simple",
            "filename": os.path.join(LOG_DIR, "logs/info.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detail",
            "filename": os.path.join(LOG_DIR, "logs/errors.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
    },

    "loggers": {
        'services': {
            "handlers": ["console", "debug_file_handler", "info_file_handler", "error_file_handler"],
            'level': 'DEBUG',
            'propagate': False,
        },
        "": {
            "level": "INFO",
            "handlers": ["console", "info_file_handler", "error_file_handler"]
         }
    },
}

logging.config.dictConfig(LOGGING)
