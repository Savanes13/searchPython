from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = 'postgresql+psycopg://postgres:2004@localhost:5432/catalog'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
  pass