import logging
import sys

from colorama import Fore


class Logger(logging.LoggerAdapter):
    def __init__(self, logger_name="sparrot", extra=None):
        self.logger = logging.getLogger(logger_name)
        self.extra = extra

    def error(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.RED}[!]{Fore.RESET} {msg}", kwargs)
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.YELLOW}[?]{Fore.RESET} {msg}", kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.BLUE}[i]{Fore.RESET} {msg}", kwargs)
        self.logger.info(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.GREEN}[+]{Fore.RESET} {msg}", kwargs)
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.CYAN}[d]{Fore.RESET} {msg}", kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def ask(self, msg, *args, **kwargs):
        msg, kwargs = self.process(f"{Fore.YELLOW}[q]{Fore.RESET} {msg} (y/N) ", kwargs)

        print(msg, end="")
        while True:
            user_input = input().lower()
            if user_input == "y":
                return True
            else:
                return False


def setup_logger(level, logger_name="sparrot"):
    formatter = logging.Formatter("%(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.addHandler(stream_handler)

    logger.setLevel(level)

    return logger
