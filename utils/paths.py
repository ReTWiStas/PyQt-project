import sys
import os


def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу для работы и из собранного exe """
    try:
        # PyInstaller создает временную папку _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)