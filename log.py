#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""

"""
import os
import logging
import logging.handlers


__all__ = ["init_logging", "setup_logger", "get_logger"]


class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


class CustomLogger(object):
    _INSTANCE = None

    def __init__(self, log_dir, log_level):
        log_level = self.to_level(log_level)

        self.log_dir = log_dir
        self.log_level = log_level
        self._init_formatters()
        self._init_handlers()
        self._init_root_logger()

    @classmethod
    def instance(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(*args, **kwargs)
        return cls._INSTANCE

    @classmethod
    def str2level(cls, ss):
        mappings = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "warn": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "notset": logging.NOTSET,
        }
        return mappings[ss.lower()]

    @classmethod
    def to_level(cls, level):
        if isinstance(level, str):
            return cls.str2level(level)
        else:
            return level

    @classmethod
    def level2str(cls, level):
        return logging.getLevelName(level)

    def _init_formatters(self):
        simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.simple_formatter = logging.Formatter(simple_format)

        detail_format = "%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)10s() ]: %(levelname)-8s %(message)s"
        self.detail_formatter = logging.Formatter(detail_format)

    def new_formatter(self, name, format_ss):
        formatter = logging.Formatter(format_ss)
        setattr(self, name, formatter)

    def _init_handlers(self):
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.detail_formatter)
        self.console_handler = handler

        info_file_args = {
            "filename": os.path.join(self.log_dir, "info.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
        handler = logging.handlers.RotatingFileHandler(**info_file_args)
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.simple_formatter)
        handler.addFilter(InfoFilter())
        self.info_file_handler = handler

        error_file_args = {
            "filename": os.path.join(self.log_dir, "errors.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
        handler = logging.handlers.RotatingFileHandler(**error_file_args)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(self.detail_formatter)
        self.error_file_handler = handler

    # def new_handler(self, name, dic):
    #     cls = dic.pop("class")
    #     cls = eval(cls)

    #     level = dic.pop("level")
    #     level = self.to_level(level)

    #     filters = dic.pop("filters", [])
    #     formatter = dic.pop("formatter")

    #     handler = cls(**dic)
    #     handler.setLevel(level)
    #     for ft in filters:
    #         ft = eval(ft)
    #         handler.addFilter(ft())
    #     setattr(self, name, handler)

    def _init_root_logger(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(self.console_handler)
        root_logger.addHandler(self.info_file_handler)
        root_logger.addHandler(self.error_file_handler)

    def setup_logger(self, logger, log_level=logging.INFO, handlers=None):
        if handlers is None:
            handlers = ["console", "info_file_handler", "error_file_handler"]
        log_level = self.to_level(log_level)

        mappings = {
            "console_handler": self.console_handler,
            "info_file_handler": self.info_file_handler,
            "error_file_handler": self.error_file_handler,
        }
        for handler in handlers:
            if handler not in mappings:
                continue
            logger.addHandler(mappings[handler])
        logger.setLevel(log_level)
        logger.propagate = False
        return logger

    def get_logger(self, name, log_level=logging.INFO, handlers=None):
        logger = logging.getLogger(name)
        logger = self.setup_logger(logger, log_level, handlers)
        return logger


def init_logging(log_dir, log_level):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    CustomLogger.instance(log_dir, log_level)


def setup_logger(logger, log_level=logging.INFO, handlers=None):
    inst = CustomLogger.instance()
    return inst.setup_logger(logger, log_level, handlers)


def get_logger(name, log_level=logging.INFO, handlers=None):
    inst = CustomLogger.instance()
    return inst.get_logger(name, log_level, handlers)


if __name__ == '__main__':
    def _test():
        init_logging("/tmp/logger_test", "Debug")
        root_logger = logging.getLogger()
        print root_logger.name, root_logger.handlers, root_logger.level
        root_logger.debug("debug message from root")
        root_logger.info("info message from root")
        root_logger.warn("warn message from root")
        root_logger.error("error message from root")

        child_logger = logging.getLogger("child")
        setup_logger(child_logger, "info", ["console_handler",])
        # child_logger.propagate = False
        print child_logger.name, child_logger.handlers, child_logger.level
        child_logger.debug("debug message from child")
        child_logger.info("info message from child")
        child_logger.warn("warn message from child")
        child_logger.error("error message from child")
    _test()
