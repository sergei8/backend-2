""" извлекает из страницы "Викладацький склад" сведения о преподавателе:
    - ссылка на фото
    - ФИО
    дописывает эти сведения в файл `time-table.json`
"""

from os import name
import sys
sys.path.insert(0, '.')

#######################
import json
import bs4
from config_app import KNTEU_URL, KAFEDRA, FACULTET, SKLAD, TIME_TABLE_FILE
from helpers import clean_string, lat_to_cyr, fix_apostroph, complex_name
from typing import Any, Dict, List, Tuple, Union   
from requests.api import options
import requests
from requests import Response
from bs4 import BeautifulSoup as bs
import re

NO_PHOTO = "no-photo"

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
        if len(name.split()) != 3:
            # имя не распарсено - забиваем пробелами
            self.last_name, self.first_name, self.middle_name = ('', '', '')
        else:
            self.last_name   = name.split(' ')[0].strip().upper()       # Фамілія
            self.first_name  = name.split(' ')[1].strip().upper()       # Имя
            self.middle_name = name.split(' ')[2].strip().upper()       # Отчество
    # привести линки на фотки к стандартному виду
        if 'http' in picture_url:
            url_splited: List[str] = picture_url.split('edu.ua')
            if len(url_splited) == 2:
                self.picture_url = url_splited[1]
            else:
                self.picture_url = NO_PHOTO
                self.__print_warning(
                    f"{name} - ошибка парсинга: {picture_url}")
        elif 'data' in picture_url:
            self.picture_url = NO_PHOTO
            self.__print_warning(f"{name} - img = data")
        elif picture_url == '':
            self.picture_url = NO_PHOTO
            self.__print_warning(f"{name} - нет фотки")
        else:
            self.picture_url = f"{KNTEU_URL}{picture_url}"       # url фотки

    def __print_warning(self, msg: str):
        print(f"\n\t{msg}", end=" ")


facs_list: List[Facultet]


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
    # выставлякмся на верхний  `<li>` для фак-та
    li_tag: bs = fac_tag.parent

    # проходим по  `li` c `a` и выбираем названия кафедр
    while(1):

        dep_tag: bs = li_tag.find_next('li')
        if dep_tag == None:
            break

        a_tag: bs = dep_tag.find('a', {"class": "att-menu-item"})
        if a_tag == None:
            break

        # если в названии есть каф-ра то вырезаем и н пкапливаем назву и линк
        if KAFEDRA in a_tag.text.split():
            name: str = a_tag.text
            url: str = a_tag.get('href')
            dep_list.append(Department(name, url))
            li_tag = a_tag
            continue

        # если след. фак-т то заканчиваем
        elif FACULTET in a_tag.text.split():
            break

        elif a_tag.text == '\n':
            li_tag = a_tag
            continue

    return dep_list


def make_teacher_list(vikl_url: str) -> List[Teacher]:
    """возвращает список инстансов преподавателей
    полученный парсингом soup vikl_page
    """

    vikl_page: str = requests.get(f"{KNTEU_URL}{vikl_url}").content
    vikl_soup: bs = bs(vikl_page, features="lxml")

    # # преподаватели находятся в таблице после a-тега "Викладацький склад"
    # if vikl_soup.find('a', text=SKLAD):
    #     teacher_table_tag: bs = vikl_soup.find('a', text=SKLAD).find_next('table')
    # else:
    #     return []

    # получить список всех td-тегов из ВСЕХ таблиц на странице
    td_tags_list: List[bs] = vikl_soup.find_all('td')

    # список реквизитов преподавателей
    teacher_list: List[Teacher] = []

    # список td-тегов, которые не соотв. стандартному
    non_standart_td: List[bs] = []

    for td_tag in td_tags_list:
        name, picture_url = extract_teacher_info(td_tag)

        if (name, picture_url) == (None, None):
            # пустая ячейка - не обрабатываем
            continue
        elif name == None or picture_url == None:
            # накопим для дальнейшего анализа
            non_standart_td.append(td_tag)
            continue

        teacher_list.append(Teacher(name, picture_url))

    # попытка вытащить из нестандартных ячеек реквизиты преподов
    for i in range(len(non_standart_td) - 1):
        _, picture_url = extract_teacher_info(non_standart_td[i])
        # если в ячейке есть `picture_url` то в следующей может быть имя
        name, _ = extract_teacher_info(non_standart_td[i + 1])

        # если вытащили реквизиты, то добавим их в выходной
        if picture_url and name:
            teacher_list.append(Teacher(name, picture_url))

    return teacher_list


def get_vikl_sklad_href(dep_page: bs) -> str:
    """ищет на странице кафедры ссылку на `Викладацький склад`
    и возвращает ее или `` если не найдено
    """
    a_tag = dep_page.find('a', text=re.compile(SKLAD))
    if a_tag != None:
        return a_tag.attrs["href"]

    return ''


def extract_teacher_info(td_tag: bs) -> Tuple[str, str]:
    """возвращает из ячейки таблицы имя и линк на фото препода 
    если за 1-ю попытку (attempt=1) не удается, то 2-й попыткой
    добирается инфа из следующей ячейки
    """

    name, url = None, None

    # пустой тег
    if td_tag == None:
        return (None, None)

    # поиск url фотки
    img_tag: bs = td_tag.find('img')
    if img_tag != None:
        # вытягиваем url фотки
        url: str = img_tag['src']

    # поиск имени в a-теге. если нету, то возвращаем только url фотки
    tags_a: List[bs] = td_tag.find_all('a')
    if len(tags_a) == 0:
        return (None, url)

    # иначе вытягиваем ФИО
    name = ""
    for tag_a in tags_a:
        name += tag_a.text

    name = ' '.join(name.split())

    return (name, url)

def get_teacher_key(name_key: str, time_table) -> Union[str, None]:
    """возвражает ключ записи препода из `time-table` или none
    """
    # поправить апостроф
    mame_key = fix_apostroph(name_key)
    
    # подправить фамілію через '-' 
    name_key = complex_name(name_key)
    
    for teacher in time_table.keys():
        if name_key in teacher:
            return teacher
    
    return None

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
    menues: List[bs] = main_page_body.find_all(
        'ul', {"class": "dropdown-menu"})
    # выделить выпадающее меню `факультеты и кафедры` (2-е)
    facs_deps_menu: bs = menues[1]

    # построить список инстансов факультетов
    facs_list = make_fac_list(facs_deps_menu)
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
            print(f"   {dep.name}", end=" : ")
            # получить главную страницу кафедры
            dep_page: Response = requests.get(f"{KNTEU_URL}{dep.url}")
            if dep_page.status_code != 200:
                print(f"Ошибка чтения страницы кафедры: {dep.name}")
                continue

            dep_page_bs: bs = bs(dep_page.content, features="lxml")

            # получить ссылку на страницу викладачей
            vikl_url: str = get_vikl_sklad_href(dep_page_bs)
            if vikl_url == '':
                print(
                    f"Не найдена ссылка на страницу преподов кафедры {dep.name}")
                continue

            # построить список преподавателей
            dep.teachers = make_teacher_list(vikl_url)
            print(len(dep.teachers))

    with open(TIME_TABLE_FILE) as f:
        time_table: Dict[str, Any] = json.loads(f.read())

    # формировать поле `details` для каждого прпода
    print("Формирую `details`")
    for fac in facs_list:
        for dep in fac.deps:
            for teacher in dep.teachers:
                details = {
                    "img_url": teacher.picture_url,
                    "name": f"{teacher.last_name} {teacher.first_name} {teacher.middle_name}",
                    "dep": dep.name,
                    "fac": fac.name
                }
                
                # формируем ключ для поиска препода в `time-table`
                last_name_key   =  teacher.last_name.capitalize()
                first_name_key  = teacher.first_name[:1].upper()
                middle_name_key = teacher.middle_name[:1].upper()
                name_key = f"{last_name_key} {first_name_key} {middle_name_key}"
                
                # искать ключ записи препода в `time-table`
                teacher_key = get_teacher_key(name_key, time_table)
                if teacher_key != None:
                    # если ключ найден - обновляем поле `details` в `time-table`
                    time_table[teacher_key]["details"] = details
                else:
                    print(f"{name_key}: {fac.name}, {dep.name} - не найден")

    # перезаписать `time-table.json`
    with open('time-table-new.json', 'w') as f:
        f.write(json.dumps(time_table, indent=2, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    main()
