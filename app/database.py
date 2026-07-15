from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import config

engine = create_engine(config.db_url, connect_args=config.db_connect_args, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
