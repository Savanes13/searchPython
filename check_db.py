from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    version = conn.execute(text("SELECT version()")).scalar()
    print("Подключение работает:", version)