import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from database.db_session import get_session
from database.models import Employee
from face_recognition.recognizer import ArcFaceRecognizer
from face_recognition.detector import YuNetDetector
import config

def main():
    if len(sys.argv) != 3:
        print("Usage: python register_employee.py <name> <image_path>")
        sys.exit(1)

    name = sys.argv[1]
    img_path = sys.argv[2]

    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        sys.exit(1)

    img = cv2.imread(img_path)
    if img is None:
        print("Cannot read image (corrupted or unsupported format)")
        sys.exit(1)

    # Используем YuNet детектор из проекта
    detector = YuNetDetector(config.YUNET_MODEL_PATH)
    bboxes = detector.detect(img)
    
    if len(bboxes) == 0:
        print("No face detected in the image")
        sys.exit(1)

    # Берём первое лицо
    x, y, w, h = bboxes[0]
    x1, y1, x2, y2 = x, y, x + w, y + h

    # Защита от выхода за границы
    h_img, w_img = img.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w_img, x2), min(h_img, y2)

    if x2 <= x1 or y2 <= y1:
        print("Invalid face region")
        sys.exit(1)

    face_crop = img[y1:y2, x1:x2]
    if face_crop.size == 0:
        print("Empty face crop")
        sys.exit(1)

    recognizer = ArcFaceRecognizer()
    embedding = recognizer.get_embedding(face_crop)

    session = get_session()
    existing = session.query(Employee).filter(Employee.name == name).first()
    if existing:
        print(f"Employee '{name}' already exists (id={existing.id}). Delete or rename.")
        session.close()
        sys.exit(1)

    emp = Employee(name=name, face_embedding=embedding)
    session.add(emp)
    session.commit()
    print(f"Employee '{name}' registered successfully with id={emp.id}")
    session.close()

if __name__ == "__main__":
    main()