from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base as _Base

engine = create_engine(settings.db_url, connect_args=settings.db_connect_args, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _Base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
