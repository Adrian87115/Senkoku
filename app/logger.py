import os
import sys
import threading
import logging
import functools
import warnings

def setup_logging():
    log_dir = os.path.join(os.getenv("APPDATA", "."), "Senkoku")
    os.makedirs(log_dir, exist_ok = True)
    log_path = os.path.join(log_dir, "crash.log")

    logger = logging.getLogger("Senkoku")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_path, mode = "w", encoding = "utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(module)s | %(funcName)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(file_formatter)
    logger.addHandler(console_handler)

    logging.captureWarnings(True)
    warnings.simplefilter("always")

    logger.info("===== Application start =====")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Executable: {sys.executable}")
    logger.info(f"Args: {sys.argv}")

    def log_exception(exc_type, exc_value, exc_tb):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = log_exception

    def thread_exception_handler(args):
        logger.error("Thread exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
    threading.excepthook = thread_exception_handler

    return logger

logger = setup_logging()

# decorater to catch errors for selected functions
def log_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__} | args = {args} kwargs = {kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} | result = {result}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}")
            raise

    return wrapper