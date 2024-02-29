import logging
from colorlog import ColoredFormatter

log_file_path = "app.log"

def setup_logger(file_mode="a"):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.propagate = False

    # Check if handlers are already added to avoid duplication
    if not logger.handlers:
        # Create a file handler with the specified mode
        file_handler = logging.FileHandler("app.log", mode=file_mode)

        # Create a colored formatter for the console
        console_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )

        # Create a regular formatter for the file
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Set formatters for the handlers
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
