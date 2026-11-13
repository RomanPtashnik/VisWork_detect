from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
from database.db_session import get_session
from database.crud import authenticate_admin

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход администратора")
        self.setModal(True)
        layout = QVBoxLayout(self)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")
        layout.addWidget(self.error_label)

    def login(self):
        sess = get_session()
        try:
            ok = authenticate_admin(sess, self.username.text(), self.password.text())
            if ok:
                self.accept()
            else:
                self.error_label.setText("Неверный логин или пароль")
        finally:
            sess.close()