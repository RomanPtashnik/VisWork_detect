import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_session import get_session
from database.models import User
from passlib.hash import pbkdf2_sha256

session = get_session()
admin = User(username="admin", password_hash=pbkdf2_sha256.hash("admin123"))
session.add(admin)
session.commit()
session.close()
print("Admin added")