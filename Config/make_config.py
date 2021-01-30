""" формирует файл config.json структуры:
<имя фак-та>: [<список ссылок на расписания по курсам (1..5)]
парсит страницу с расписанием студентов и выбирает href на экселл-файл
c расписанием
"""
import typing
import requests
from bs4 import BeautifulSoup as bs

TIME_TABLE_URL = "https://knute.edu.ua/blog/read/?pid=1038&uk"

def get_timetable_page():
    """возвращает Respond страницы расписания
    """
    resp = requests.get(TIME_TABLE_URL)
    
    return resp if resp.status_code == 200 else None

def get_parsed_timetable():
    pass
    return None
    
