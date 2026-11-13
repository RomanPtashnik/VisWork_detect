import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_session import engine, Base
from database import models # <-- Важно: импортируем модели, чтобы зарегистрировать их в Base

def init_database():
    print("Creating database tables...")
    # Создаём все таблицы, описанные в моделях
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Tables created successfully!")

if __name__ == "__main__":
    init_database()