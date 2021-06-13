"""
конфигурационный файл для приложения
"""

TIME_TABLE_URL = "https://knute.edu.ua/blog/read/?pid=1038&uk"
CONFIG_JSON = "config.json"
GROUPS_JSON = "groups.json"
KNTEU_URL = "https://knute.edu.ua"

# название листа с расписанием
NAME_OF_WS = [
    "розклад"
]

# паттерны для поиска
WEEK_NOMER = r"Перший"
# WEEK_NOMER = r"Перший\W+тиждень"
# WEEK_NOMER = r"Номер\W+тижня"
DAY_NAME = "День\nтижня"
GROUP = r"група"
KAFEDRA = "Кафедра"
FACULTET = "Факультет"
SKLAD = "Викладацький склад"