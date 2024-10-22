import logging
import os
from dotenv import load_dotenv

# Setup logging to file and console
logging.basicConfig(level=logging.DEBUG,  # Set to DEBUG for detailed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('test_log.txt'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger()


# Function to test logging
def test_logging():
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")


if __name__ == "__main__":
    test_logging()