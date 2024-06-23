import logging
import logging.handlers
import os

LOG_PATH = "../logs/"


def setup_logger(name, log_file, level=logging.INFO):
    """
    Configure and return a logger.

    Args:
        name (str): The name of the logger.
        log_file (str): The file to which the log messages will be written.
        level (int, optional): The logging level (e.g., logging.DEBUG, logging.INFO, etc.). Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger.
    """

    logger = logging.getLogger(name)

    # Check if the logger has handlers already to avoid adding them multiple times
    if not logger.hasHandlers():
        # Ensure the directory exists
        log_dir = os.path.dirname(LOG_PATH + log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        handler = logging.FileHandler(LOG_PATH + log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

        logger.setLevel(level)
        logger.addHandler(handler)

    return logger

