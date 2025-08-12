import logging
import sys

# Configure the logger to output to both console and file with a specific format
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter(
    "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    )

# Create handlers for console and file output
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]
