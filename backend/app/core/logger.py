import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# file handler
file_handler = logging.FileHandler("backend.log", mode="a")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# console (stream) handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# attach
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# SQLAlchemy
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.WARNING)