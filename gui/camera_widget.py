import time
import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap
from face_recognition.detector import YuNetDetector
from face_recognition.recognizer import ArcFaceRecognizer
from database.crud import find_employee_by_embedding, record_attendance
from database.db_session import get_session
import config

class CameraWidget(QWidget):
    face_recognized = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.detector = YuNetDetector(config.YUNET_MODEL_PATH)
        self.recognizer = ArcFaceRecognizer()

        self.last_recognition_time = 0
        self.last_recognized_name = None
        self.last_recognized_time = 0
        self.display_name_timeout = 2.0

    def start_camera(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            return False
        self.timer.start(config.DETECTION_INTERVAL_MS)
        return True

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def update_frame(self):
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        bboxes = self.detector.detect(frame)

        # Если есть лицо в кадре, возможно, нужно распознать
        now = time.time()
        if bboxes and (now - self.last_recognition_time) >= config.RECOGNITION_COOLDOWN_SEC:
            # Берём первое лицо для распознавания (можно улучшить: самое большое)
            x, y, w, h = bboxes[0]
            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size > 0:
                self.last_recognition_time = now
                self.process_face(face_roi)

        # Отображаем рамки и имена
        for (x, y, w, h) in bboxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Решаем, какое имя показывать
            name_to_show = None
            # Если есть недавно распознанное имя (таймаут)
            if self.last_recognized_name and (now - self.last_recognized_time) <= self.display_name_timeout:
                name_to_show = self.last_recognized_name
            else:
                name_to_show = None

            if name_to_show:
                cv2.putText(frame, name_to_show, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        scaled = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled)

    def process_face(self, face_img):
        embedding = self.recognizer.get_embedding(face_img)
        session = get_session()
        try:
            employee = find_employee_by_embedding(session, embedding, config.FACE_MATCH_THRESHOLD)
            now = time.time()
            if employee:
                # Обновляем кеш имени и времени
                self.last_recognized_name = employee.name
                self.last_recognized_time = now

                result, timestamp, worked = record_attendance(session, employee.id, config.LUNCH_BREAK_MINUTES)
                if result == 'check_in':
                    msg = f"Приход: {employee.name} в {timestamp.strftime('%H:%M:%S')}"
                elif result == 'check_out':
                    msg = f"Уход: {employee.name} в {timestamp.strftime('%H:%M:%S')}, отработано {worked:.2f} ч"
                else:
                    msg = f"{employee.name} уже отметил уход сегодня"
                self.face_recognized.emit(msg)
            else:
                self.last_recognized_name = "None"
                self.last_recognized_time = now
                self.face_recognized.emit("Лицо не распознано")
        finally:
            session.close()