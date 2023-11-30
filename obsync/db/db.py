import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError


from obsync.logger import logger
from obsync.config import config

db_file_path = os.path.join(config.DataDir, "vaults.db")
DATABASE_URL = f"sqlite:///{db_file_path}"

# NOTE Enable sqlite log: echo->INFO
engine = create_engine(DATABASE_URL, echo=False)
SessionFactory = sessionmaker(bind=engine)


Base = declarative_base()


def init_db():
    try:
        Base.metadata.create_all(engine)
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


def session_handler(func):
    def wrapper(*args, **kwargs):
        try:
            with SessionFactory() as session:
                return func(*args, **kwargs, session=session)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise

    return wrapper
