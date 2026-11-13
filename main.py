import sys
from PyQt6.QtWidgets import QApplication
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from database.db_session import init_db

def main():
    init_db()
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec() == LoginWindow.DialogCode.Accepted:
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()