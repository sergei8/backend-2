""" формирует файл config.json структуры:
<имя фак-та>: [<список ссылок на расписания по курсам (1..5)]
парсит страницу с расписанием студентов и выбирает href на экселл-файл
c расписанием
"""
from typing import Union, Any, Tuple
import requests
from bs4 import BeautifulSoup as bs

TIME_TABLE_URL = "https://knute.edu.ua/blog/read/?pid=1038&uk"
DENNA_FORMA_TABLE_NAME = "ДЕННА ФОРМА НАВЧАННЯ"

def get_timetable_page(url: str):
    """возвращает Respond страницы расписания
    """
    resp = requests.get(url)
    
    return resp if resp.status_code == 200 else None

def get_parsed_timetable(html_page) -> Union[bs, None]:
    """строит и возвращает soup-объект из страницы расписаний

    Args:
        html_page (str): объект страницы

    Returns:
         распарсеный soup или None
    """
    try:
        parsed_page = bs(html_page.content, features='html.parser')
        if not isinstance(parsed_page, bs):
            return None

    except:
        return None

    return parsed_page
    
def extract_time_tables(parsed_page) -> Tuple[bs, bs]: 
    # выделить начало секции расписания денной формы
    denna_forma:bs = parsed_page.find("strong", text=DENNA_FORMA_TABLE_NAME)
    
    # таблиц бакалавров (через одну в DOM)
    table_bakalavr:bs = denna_forma.parent.next_sibling.next_sibling

    # таблица магистров
    table_magistr:bs = table_bakalavr.next_sibling.next_sibling

    return (table_bakalavr, table_magistr)

def main():
    
    # читать страницу расписания
    time_table_page = get_timetable_page(TIME_TABLE_URL)
    if not time_table_page:
        print("ошибка чтения url расписания")
        exit(1)
    
    # распарсить страницу расписаний
    parsed_page = get_parsed_timetable(time_table_page)
    if not parsed_page:
        print("ошибка парсинга страницы расписания")
        exit(1)

    # выделить таблицу и загрузить ее в pandas
    denna_forma = extract_time_tables(parsed_page)
    # print(denna_forma)
    

if __name__ == '__main__':
    main()