import os, logging, sys

from logging import Logger
from logging.handlers import RotatingFileHandler

from logger.constants import LOGGING_PATH, MAX_ACTIVITY_LOGFILE_SIZE, MESSAGE_LEVEL
from all.constants import cmdColors

def configureFileLogging(gameName: str, logLevel: int, logger: Logger):
    logPath: str = LOGGING_PATH + gameName

    os.makedirs(logPath, mode = 0o777, exist_ok = True)

    file_handler = RotatingFileHandler(logPath + "/activity.log", mode = 'a', maxBytes = MAX_ACTIVITY_LOGFILE_SIZE, backupCount = 1)
    file_handler.setLevel(logLevel)

    file_formatter = logging.Formatter("%(asctime)s %(levelname)s | %(message)s", "%m/%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    error_handler = RotatingFileHandler(logPath + "/errors.log", mode = 'a', maxBytes = MAX_ACTIVITY_LOGFILE_SIZE, backupCount = 1)
    error_handler.setLevel(40)

    error_formatter = logging.Formatter("----------------------\n%(asctime)s [%(name)s] | %(message)s", "%m/%d %H:%M:%S")
    error_handler.setFormatter(error_formatter)

    logger.addHandler(error_handler)

class CustomConsoleFormatter(logging.Formatter):
    def format(self, record):
        # Print text in red if it's an error
        if record.levelno == logging.ERROR: log_format = f"{cmdColors.FAIL} [%(levelname)s] |{cmdColors.ENDC} %(message)s"
        else: log_format = "[%(levelname)s] | %(message)s"

        log_format += "\n>> "

        formatter = logging.Formatter(log_format)
        return formatter.format(record)

def configureConsoleLogging(logLevel: int, logger: Logger):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logLevel)
    stream_handler.terminator = ""

    stream_handler.setFormatter(CustomConsoleFormatter())

    logger.addHandler(stream_handler)
    
def welcomeMessage(self: Logger):
    """Log WELCOME_MESSAGE in the logger"""

    if self.isEnabledFor(100):
        string = """#======================================#\n\t    # Coding Game Server is going to start #\n\t    #======================================#"""
        self._log(100, string, (), {})

def message(self: Logger, msg: str, *args, **kws):
    """Log MESSAGE in the logger"""

    if self.isEnabledFor(MESSAGE_LEVEL):
        self._log(MESSAGE_LEVEL, msg, args, **kws)

def error(self: Logger, msg: str, *args, **kws):
    """Log ERROR in the logger"""

    if self.isEnabledFor(40):
        self._log(40, msg, args, **kws)
        sys.exit()