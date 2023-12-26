import logging
import sys


def setup_logger(name, log_file, level=logging.INFO):
    """
    Set up a logger with specified name, log file, and level.

    Args:
    - name: The name of the logger.
    - log_file: The file name for the log file.
    - level: The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
    - logger: The configured logger.
    """
    # Create a logger with the given name
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatters for logging
    formatter = logging.Formatter(
        "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Setup file handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Example usage
log = setup_logger("log", "run.log", level=logging.DEBUG)
log.info("Logger setup complete.")
