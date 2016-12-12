#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
custom logging configuration
usage:
1. call init_logging at the beginning of your program, you can use
   `new_formatter`, `new_filter` and `new_handler` to add your own formatter,
   filters and handlers
2. in other module, you can call `get_logger` to get logger by name,
    you can specify the handler and level you want use for this logger(optional)
    `get_logger` is equal to `logger = logging.getLogger(name); setup_logger(logger)`
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
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_level = self.to_level(log_level)

        self.log_dir = log_dir
        self.log_level = log_level

        self._init_formatters()
        self._init_filters()
        self._init_handlers()
        self._init_root_logger()

    @classmethod
    def instance(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(*args, **kwargs)
        return cls._INSTANCE

    @classmethod
    def level2str(cls, level):
        return logging.getLevelName(level)

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
    def _is_class_type(cls, o):
        return isinstance(o, type)

    def _init_formatters(self):
        simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.simple_formatter = logging.Formatter(simple_format)

        detail_format = "%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)10s() ]: %(levelname)-8s %(message)s"
        self.detail_formatter = logging.Formatter(detail_format)

    def _init_filters(self):
        self.new_filter("info_filter", InfoFilter)

    def _init_handlers(self):
        console_handler_settings = {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detail",
        }
        self.new_handler("console_handler", console_handler_settings)

        info_file_handler_args = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filters": ["info_filter", ],
            "formatter": "simple",
            "filename": os.path.join(self.log_dir, "info.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
        self.new_handler("info_file_handler", info_file_handler_args)

        error_file_handler_args = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "detail",
            "filename": os.path.join(self.log_dir, "errors.log"),
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
        self.new_handler("error_file_handler", error_file_handler_args)

    def _str2obj(self, name):
        parts = name.split(".")
        try:
            root = globals()[parts[0]]
        except:
            root = getattr(self, name)

        for part in parts[1:]:
            root = getattr(root, part)
        return root

    def new_formatter(self, name, format_ss):
        formatter = logging.Formatter(format_ss)
        if not name.endswith("_formatter"):
            name += "_formatter"
        setattr(self, name, formatter)

    def new_filter(self, name, cls):
        if isinstance(cls, str):
            cls = self._str2obj(cls)
        if not name.endswith("_filter"):
            name += "_filter"

        if self._is_class_type(cls):
            obj = cls()
        else:
            obj = cls
        setattr(self, name, obj)

    def new_handler(self, name, dic):
        cls = dic.pop("class")
        if isinstance(cls, str):
            cls = self._str2obj(cls)

        level = dic.pop("level")
        level = self.to_level(level)

        filters = dic.pop("filters", [])
        formatter_str = dic.pop("formatter")
        if not formatter_str.endswith("formatter"):
            formatter_str += "_formatter"
        formatter = getattr(self, formatter_str)

        handler = cls(**dic)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        for ft in filters:
            if isinstance(ft, str):
                ft = self._str2obj(ft)
            if self._is_class_type(ft):
                obj = ft()
            else:
                obj = ft
            handler.addFilter(obj)
        if not name.endswith("_handler"):
            name += "_handler"
        setattr(self, name, handler)

    def _init_root_logger(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(self.console_handler)
        root_logger.addHandler(self.info_file_handler)
        root_logger.addHandler(self.error_file_handler)

    def setup_logger(self, logger, log_level=logging.INFO, handlers=None):
        if handlers is None:
            handlers = [
                "console_handler", "info_file_handler", "error_file_handler"
            ]
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
    CustomLogger.instance(log_dir, log_level)


def setup_logger(logger, log_level=logging.INFO, handlers=None):
    inst = CustomLogger.instance()
    return inst.setup_logger(logger, log_level, handlers)


def get_logger(name, log_level=logging.INFO, handlers=None):
    inst = CustomLogger.instance()
    return inst.get_logger(name, log_level, handlers)


def new_formamtter(formatter_name, formater_ss):
    inst = CustomLogger.instance()
    inst.new_formatter(formatter_name, formater_ss)


def new_filter(name, cls):
    inst = CustomLogger.instance()
    inst.new_filter(name, cls)


def new_handler(handler_name, dic):
    inst = CustomLogger.instance()
    inst.new_handler(handler_name, dic)


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
        setup_logger(child_logger, "info", ["console_handler", "info_file_handler", "error_file_handler"])
        # child_logger.propagate = False
        print child_logger.name, child_logger.handlers, child_logger.level
        child_logger.debug("debug message from child")
        child_logger.info("info message from child")
        child_logger.warn("warn message from child")
        child_logger.error("error message from child")
    _test()
