""" извлекает из страницы "Викладацький склад" сведения о преподавателе:
    - ссылка на фото
    - ФИО
    дописывает эти сведения в файл `time-table.json`
"""
import sys

import bs4
sys.path.insert(0, '.')
from config_app import KNTEU_URL, KAFEDRA, FACULTET, SKLAD
from helpers import clean_string

from typing import Any, List, Tuple
from requests.api import options


import requests
from requests import Response
from bs4 import BeautifulSoup as bs
import re


class Facultet:
    """класс для факультета"""

    def __init__(self, name: str, url: str):
        self.name: str = name                 # наименование
        self.url: str = url                   # url
        self.deps: List[Department] = []      # список кафедр


class Department:
    """ класс для кафедры """

    def __init__(self, name: str, url: str):
        self.name: str = name                    # название кафедры
        self.url: str = url                      # url
        self.teachers: List[Teacher] = []       # список преподавателей


class Teacher:
    """ класс для преподавателя """

    def __init__(self, name: str, picture_url: str = ''):
        self.last_name = name.split(' ')[0].strip()       # Фамілія
        self.first_name = name.split(' ')[1].strip()       # Имя
        self.middle_name = name.split(' ')[2].strip()       # Отчество
        self.picture_url = picture_url                      # url фотки


def make_fac_list(fac_dep_menu: bs) -> List[Facultet]:
    """парсит soup-меню и возвращает список инстансов 
    фак-тов с названиями и href
    """

    # выделить теги названий факультетов в список
    fac_tags = fac_dep_menu.find_all('span', {'class': 'prev-link'})

    # проход по списку тегов названий и выделение из их
    # родителя (a-тега) названия и url факультета
    # создание инстанса Facultet и заненсенее его в список
    facultets = []
    for tag in fac_tags:
        name: str = tag.parent.find('span').text
        url: str = tag.parent.get('href')
        facultets += [Facultet(name, url)]

    return facultets


def make_dep_list(fac_name: str, menu: bs) -> List[Department]:
    """получает название фак-та, ищет его в soup-меню 
    и парсит все кафедры фак-та и их href
    возвращает список инстансов кафедр
    """

    dep_list: List[Department] = []

    # находим таг с назв.фак-та
    fac_tag: bs = menu.find('a', text=fac_name)
    if fac_tag == None:
        print(f"\nНе найдены кафедры по факультету: {fac_name}")
        exit(1)
    # выставлякмся на верхний  `<li>`
    li_tag: bs = fac_tag.parent

    # проходим по  `li` c `a` и выбираем названия кафедр
    # TODO: при проходе ФФО попадаю в бесконечный цикл
    while(1):

        dep_tag: bs = li_tag.find_next('li')
        if dep_tag == None:
            break
        
        a_tag:bs = dep_tag.find('a')
        if a_tag == None:
            break
            
        if KAFEDRA in a_tag.text.split():
            name:str = a_tag.text
            url:str = a_tag.get('href')
            dep_list.append(Department(name, url))
            li_tag = a_tag
            continue
        elif FACULTET in a_tag.text.split():
            break
        elif a_tag.text == '\n':
            li_tag = a_tag
            continue

    return dep_list


def make_teacher_list(vikl_page: str) -> List[Teacher]:
    """возвращает список инстансов преподавателей
    полученный парсингом soup vikl_page
    """
    # преподаватели находятся в таблице после a-тега "Викладацький склад"
    if vikl_page.find('a', text=SKLAD):
        teacher_table_tag: bs = vikl_page.find('a', text=SKLAD).find_next('table')
    else:
        return []

    # получить список всех td-тегов из таблицы
    td_tags_list: List[bs] = teacher_table_tag.find_all('td')

    # формируем выходной список проходя по всем ячейкам таблицы
    teacher_list: List[Teacher] = []
    for td_tag in td_tags_list:
        name, picture_url = extract_teacher_info(td_tag)
        if (name, picture_url) == (None, None):
            continue
        teacher_list.append(Teacher(name, picture_url))

    return teacher_list


def get_vikl_sklad_href(dep_page: bs) -> str:
    """ищет на странице кафедры ссылку на `Викладацький склад`
    и возвращает ее или `` если не найдено
    """
    a_tag = dep_page.find('a', text=SKLAD)
    if a_tag != None:
        return a_tag.attrs["href"]

    return ''
 

def extract_teacher_info(td_tag: bs) -> Tuple[str, str]:
    """возвращает из ячейки таблицы имя и линк на фото препода
    """
    # поиск имени в a-теге
    tag_a: bs = td_tag.find('a')
    if tag_a == None:
        return (None, None)
    name: str = tag_a.text
    name = ' '.join(name.split())

    # поиск url
    url: str = td_tag.find('img')["src"]

    return (name, url)
    


def main() -> int:

    # открыть главную страницу
    print("\nполучаю главную страницу")
    main_page: Response = requests.get(KNTEU_URL)
    if main_page.status_code != 200:
        print(f"\nошибка чтения {KNTEU_URL}")
        exit(1)

    # получить bs-объект
    soup_main_page = bs(main_page.content, features='html.parser')
    # выделить `body`-контент
    main_page_body = soup_main_page.body
    # выделить контент главного меню
    menues: List[bs] = main_page_body.find_all('ul', {"class": "dropdown-menu"})
    # выделить выпадающее меню `факультеты и кафедры` (2-е)
    facs_deps_menu:bs = menues[1]

    # построить список инстансов факультетов
    facs_list: List[Facultet] = make_fac_list(facs_deps_menu)
    print("Список факультетов")

    # построить список инстансов кафедр для каждоо фак-та
    for fac in facs_list:
        print(f"*** {fac.name}")
        fac.deps = make_dep_list(fac.name, facs_deps_menu)
    
    print("Список кафедр")
       
    # построить список инстансов преподавателей для каждой кафедры
    for fac in facs_list:
        print(f"{fac.name}")
        
        for dep in fac.deps:
            print(f"   {dep.name}")    
            # получить главную страницу кафедры
            dep_page: Response = requests.get(dep.url)
            if dep_page.status_code != 200:
                print (f"Ошибка чтения страницы кафедры: {dep.name}")
                continue
            
            dep_page_bs: bs = bs(dep_page.content, features="parser.html")
            
            # получить ссылку на страницу викладачей
            vikl_url: str = get_vikl_sklad_href(dep_page_bs)
            if vikl_url == '':
                print(f"Не найдена ссылка на страницу преподов кафедры {dep.name}")
                continue
            
            # построить список преподавателей
            dep.teachers = make_teacher_list(vikl_url)
            
        
    

    return 0


if __name__ == '__main__':
    main()
