"""
конфигурационный файл для приложения
"""

TIME_TABLE_URL = "https://knute.edu.ua/blog/read/?pid=1038&uk"
TIME_TABLE_FILE = "time-table.json"
CONFIG_JSON = "config.json"
GROUPS_JSON = "groups.json"
KNTEU_URL = "https://knute.edu.ua"

# название листа с расписанием
NAME_OF_WS = [
    "розклад"
]

# паттерны для поиска
WEEK_NOMER = r"Перший"
DAY_NAME = "День\nтижня"
GROUP = r"група"
KAFEDRA = "Кафедра"
FACULTET = "Факультет"
SKLAD = ["Викладацький склад", "Склад кафедри"]