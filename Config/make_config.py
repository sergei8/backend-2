""" формирует файл config.json структуры:
<имя фак-та>: [<список ссылок на расписания по курсам (1..5)]
парсит страницу с расписанием студентов и выбирает href на экселл-файл
c расписанием
"""
import os
import sys
sys.path.insert(0, os.getcwd())

from config_app import TIME_TABLE_URL, CONFIG_JSON
from typing import List, Union, Any, Tuple,AnyStr, Dict
import requests
from requests import Response
from bs4 import BeautifulSoup as bs, StopParsing
from bs4 import Tag
from collections import OrderedDict
import json

DENNA_FORMA_TABLE_NAME = "ДЕННА ФОРМА\nНАВЧАННЯ"


def get_timetable_page(url: str) -> Union[Response, None] :
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

    def find_time_table_tag(level_name: AnyStr) -> bs:
        for elem in denna_forma.next_elements:
            # for each tag do check for eq `level_name`
            if isinstance(elem, Tag):
                if elem.text == level_name:
                    # find first next table
                    return elem.find_next('table')
        return ""

    # выделить начало секции расписания денной формы
    denna_forma: bs = parsed_page.find("strong", text=DENNA_FORMA_TABLE_NAME)

    # таблиц бакалавров
    table_bakalavr: bs = find_time_table_tag("БАКАЛАВР")

    # таблица магистров
    table_magistr: bs = find_time_table_tag("МАГІСТР")

    return (table_bakalavr, table_magistr)


def get_time_table_list(table_tag: bs) -> list:
    time_table_list = table_tag.find_all('tr')
    return time_table_list

def make_output_json_keys(list_keys: list[Tag]) -> dict[str, Any]:
    list_of_keys = [k.text for k in list_keys.find_all('td')]

    return OrderedDict.fromkeys(list_of_keys)

def make_output_json_values(tr_tags: List[Tag]) -> List[List[str]]:
    output = []

    for tr_tag in tr_tags:
        output.append([a.get('href') for a in tr_tag.find_all('a')])

    return output

def make_final_json(output: Dict[str, Any], values: list[List[str]]) -> dict[str, List[Any]]:

    # транспонировать массив `values`
    transposed_values = map(list, zip(*values))

    # получить и отдать результатный словарь
    return dict(zip(output, transposed_values))


def main() -> None:

    # читать страницу расписания
    print("\nчитаю url...")
    time_table_page = get_timetable_page(TIME_TABLE_URL)
    if not time_table_page:
        print("ошибка чтения url расписания")
        exit(1)
    print("страница получена...")

    # распарсить страницу расписаний
    parsed_page = get_parsed_timetable(time_table_page)
    if not parsed_page:
        print("ошибка парсинга страницы расписания")
        exit(1)

    # выделить теги таблиц бакалавров и магистров
    soup_table_bakalavr, soup_table_magistr = extract_time_tables(parsed_page)
    print("парсинг...")

    # получить списки из тегов таблиц
    list_table_bakalavr: List[Tag] = get_time_table_list(soup_table_bakalavr)
    list_table_magistr:  List[Tag] = get_time_table_list(soup_table_magistr)

    # слить 2 списка без первых строк - будет список ссылок на файлы
    list_values: List[Tag] = list_table_bakalavr[1:] + list_table_magistr[1:]

    #  список назв. факультетов
    list_keys: List[Tag] = list_table_bakalavr[0]

    # формировать ключи для выходного json
    output_json: dict[str, Any] = make_output_json_keys(list_keys)
    print(f"{list(output_json.keys())}")

    # формировать значение для выходного json
    output_json_values: list[List[str]] = make_output_json_values(list_values)

    # заполнить json ссылками на файлы с расписанием
    output_json: dict[str, list[str]] = make_final_json(
        output_json, output_json_values)

    # записать результатный файл
    with open(CONFIG_JSON, 'w', encoding="utf-8") as output:
        json.dump(output_json, output, indent=2, ensure_ascii=False)

    print(f"файл записан\n\n")


if __name__ == '__main__':
    main()
