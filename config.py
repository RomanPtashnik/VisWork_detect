import os
from dotenv import load_dotenv

load_dotenv()
# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
YUNET_MODEL_PATH = "models/face_detection_yunet_2023mar.onnx"

# Recognition settings
FACE_MATCH_THRESHOLD = 0.6      # косинусное расстояние (меньше = строже)
LUNCH_BREAK_MINUTES = 60        # обеденный перерыв в минутах

# Camera
CAMERA_ID = 0

# Processing
DETECTION_INTERVAL_MS = 100     # интервал обновления кадра (мс)
RECOGNITION_COOLDOWN_SEC = 15.0  # задержка между распознаваниями (сек)


'''
FastAPI
'''
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))