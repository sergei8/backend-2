""" формирует файл config.json структуры:
<имя фак-та>: [<список ссылок на расписания по курсам (1..5)]
парсит страницу с расписанием студентов и выбирает href на экселл-файл
c расписанием
"""

from typing import List, Dict
import requests
from bs4 import BeautifulSoup as bs

TIME_TABLE_URL = "https://knute.edu.ua/blog/read/?pid=1038&uk"

def get_timetable_page():
    """возвращает Respond страницы расписания
    """
    return requests.get(TIME_TABLE_URL)

def get_parsed_timetable():
    pass
    


def main():
    pass
    
    # читать страницу расписания
    
    # переходім на начало секціі распісанія
    
    # находим таблицу бакадавров и выдкляем шапку
    
    
    # извлечение url эксел файлов 