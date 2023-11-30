import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")
logger.add("log/error.log", level="WARNING", encoding="utf8")
