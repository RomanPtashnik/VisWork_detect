from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox
from PyQt6.QtCore import QTimer
from .camera_widget import CameraWidget
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition System")
        self.setGeometry(100, 100, 800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.camera_widget = CameraWidget()
        layout.addWidget(self.camera_widget, stretch=1)

        control = QHBoxLayout()
        self.settings_btn = QPushButton("Настройки")
        self.logout_btn = QPushButton("Выйти")
        control.addWidget(self.settings_btn)
        control.addWidget(self.logout_btn)
        layout.addLayout(control)

        self.status_label = QLabel("Готов")
        layout.addWidget(self.status_label)

        self.camera_widget.face_recognized.connect(self.update_status)
        self.logout_btn.clicked.connect(self.logout)
        self.settings_btn.clicked.connect(self.open_settings)

        self.camera_widget.start_camera(config.CAMERA_ID)

    def update_status(self, msg):
        self.status_label.setText(msg)
        QTimer.singleShot(3000, lambda: self.status_label.setText("Готов"))

    def logout(self):
        self.camera_widget.stop_camera()
        self.close()

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        form = QFormLayout(dialog)

        lunch = QSpinBox()
        lunch.setRange(0, 240)
        lunch.setValue(config.LUNCH_BREAK_MINUTES)
        lunch.setSuffix(" мин")
        form.addRow("Обеденный перерыв:", lunch)

        threshold = QDoubleSpinBox()
        threshold.setRange(0.1, 1.0)
        threshold.setSingleStep(0.05)
        threshold.setValue(config.FACE_MATCH_THRESHOLD)
        form.addRow("Порог распознавания:", threshold)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            config.LUNCH_BREAK_MINUTES = lunch.value()
            config.FACE_MATCH_THRESHOLD = threshold.value()