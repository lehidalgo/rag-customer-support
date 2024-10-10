from utils.logger import get_logger

# Initialize the logger
logger = get_logger(name=__name__, level="DEBUG")

# Use the logger
logger.info("This is an informational message.")
logger.debug("This is a debug message.")
