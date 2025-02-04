import logging

from logger.constants import MESSAGE_LEVEL
from logger.handler import configureConsoleLogging, message, error, welcomeMessage

def configureLogger(logLevel: int):
    logging.addLevelName(MESSAGE_LEVEL, "MESSAGE")
    logging.addLevelName(100, "WELCOME")
    
    logging.Logger.welcomeMessage = welcomeMessage
    logging.Logger.message = message
    logging.Logger.error = error

    logger = logging.getLogger()
    logger.setLevel(logLevel)

    configureConsoleLogging(logLevel, logger)
