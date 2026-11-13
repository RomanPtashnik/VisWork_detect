# 🎯 VisWork: Система биометрического учета рабочего времени

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-yellow.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![OpenCV](https://img.shields.io/badge/OpenCV-YuNet-red.svg)](https://opencv.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

## 📌 О проекте
Гибридная система для автоматизации учета рабочего времени сотрудников с использованием биометрической идентификации по лицу. Проект решает проблему "фальшивых отметок" и человеческого фактора, используя стандартную веб-камеру и CPU (без необходимости дорогих GPU).

**Ключевые возможности:**
*   **Десктопное приложение (PyQt6):** Захват видеопотока, детекция лиц (YuNet) и распознавание (ArcFace) в реальном времени.
*   **Логика учета:** Автоматическая фиксация прихода/ухода, расчет отработанных часов (с вычетом обеда), защита от двойной отметки (cooldown 10 сек).
*   **Веб-сервис (FastAPI):** Удаленное администрирование, CRUD сотрудников, просмотр отчетов, JWT-авторизация.
*   **Единая БД (PostgreSQL):** Мгновенная синхронизация между десктопом и веб-интерфейсом.

## 🏗 Архитектура
<img width="620" height="226" alt="image" src="https://github.com/user-attachments/assets/7aafd97f-af65-4f57-94c2-340cfc8eb46e" />

*   **Frontend:** HTML, CSS, Vanilla JS
*   **Backend:** FastAPI, SQLAlchemy, JWT
*   **Desktop:** PyQt6, OpenCV, InsightFace
*   **ML:** YuNet (детекция), ArcFace (эмбеддинги лиц, 512d)

## 📊 Результаты экспериментов
В ходе тестирования на базе из 15 сотрудников были получены следующие показатели:
*   **Точность детекции (YuNet):** Precision 0.97, Recall 0.94.
*   **Точность распознавания (ArcFace):** TPR 0.96, FAR 0.8%, FRR 4%.
*   **Производительность:** Детекция — 32 мс, извлечение эмбеддинга — 45 мс. Общая задержка < 1 сек.
