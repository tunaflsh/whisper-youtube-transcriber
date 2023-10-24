import logging


def logging_config(debug: list[str] = None) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "debug": {
                "format": "\033[34m{levelname:8}\033[0;35m{name:>25s}\033[0;2m.{funcName:30}\033[0;34m{message}\033[0m",
                "style": "{",
            },
            "info": {
                "format": "{levelname:8}\033[35m{name:>25s}\033[0;2m.{funcName:30}\033[0m{message}",
                "style": "{",
            },
            "warning": {
                "format": "\033[33m{levelname:8}\033[0;35m{name:>25s}\033[0;2m.{funcName:30}\033[0;33m{message}\033[0m",
                "style": "{",
            },
            "error": {
                "format": "\033[31m{levelname:8}\033[0;35m{name:>25s}\033[0;2m.{funcName:30}\033[0;31m{message}\033[0m",
                "style": "{",
            },
            "critical": {
                "format": "\033[35m{levelname:8}\033[0;35m{name:>25s}\033[0;2m.{funcName:30}\033[0;35m{message}\033[0m",
                "style": "{",
            },
        },
        "filters": {
            "root": {
                "()": lambda: lambda record: (
                    record.name != "root"
                    or (
                        setattr(record, "name", ""),
                        setattr(record, "funcName", ""),
                    ),
                    record,
                )[-1],
            },
        },
        "handlers": {
            "debug": {
                "class": "logging.StreamHandler",
                "formatter": "debug",
                "filters": [lambda record: record.levelno == logging.DEBUG, "root"],
            },
            "info": {
                "class": "logging.StreamHandler",
                "formatter": "info",
                "filters": [lambda record: record.levelno == logging.INFO, "root"],
            },
            "warning": {
                "class": "logging.StreamHandler",
                "formatter": "warning",
                "filters": [
                    lambda record: record.levelno == logging.WARNING,
                    "root",
                ],
            },
            "error": {
                "class": "logging.StreamHandler",
                "formatter": "error",
                "filters": [lambda record: record.levelno == logging.ERROR, "root"],
            },
            "critical": {
                "class": "logging.StreamHandler",
                "formatter": "critical",
                "filters": [
                    lambda record: record.levelno == logging.CRITICAL,
                    "root",
                ],
            },
        },
        "loggers": {
            "": {
                "handlers": ["debug", "info", "warning", "error", "critical"],
                "level": "DEBUG" if debug == [""] else "INFO",
                "propagate": False,
            },
            **{
                name: {
                    "handlers": ["debug", "info", "warning", "error", "critical"],
                    "level": "DEBUG",
                    "propagate": False,
                }
                for name in debug
                if name
            },
        },
    }
