from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.base import Base  # 👈 Укажите путь к файлу, где лежат ваши классы

from os import getenv

# Формат: postgresql+psycopg2://пользователь:пароль@хост:порт/имя_бд
DATABASE_URL = getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)  # echo=True покажет SQL-запросы в консоли

def init_db():
    Base.metadata.create_all(engine)
    
if __name__ == "__main__":
    init_db()