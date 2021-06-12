#!/usr/bin/env python
#  coding=utf-8
__author__ = 'SERGEY'

# TODO попробовать нечеткое сравнение строк: http://qaru.site/questions/52066/fuzzy-string-comparison-in-python-confused-with-which-library-to-use


from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re
import urllib
import json
from typing import List

# from string import maketrans

MAIN_PAGE = 'http://knute.edu.ua'
# патерн для шаблона ФАМИЛИЯ ИМЯ ОТЧЕСТВО или Фамилия Имя Отчество c возможнимі латінскімі
mask = "([А-ЯІЇЄ\']{1}[А-ЯІЇЄа-яіїє\']+\\s){3}"
# mask = r"([А-ЯІЇЄ\'']{1}[А-ЯІЇЄа-яіїє\'']+\\s){3}"
# mask = r'([А-ЯІЇЄACIKHTPOXBM]{1}[А-ЯІЇЄа-яіїєA-Z]+\s){3}'


# mask = r'([А-ЯІЇЄ]{1}[А-ЯІЇЄа-яіїє\’]+\s){3}'
# mask = r'([А-ЯІЇЄA-Z]){3,}\s+([А-ЯІЇЄA-Z]){1,}\s+([А-ЯІЇЄA-Za-z]){1,}\s+'

# определяем класс для факультета
class Facultet:
    def __init__(self, name, url):
        self.name = name  # наимеование
        self.url = url  # url
        self.deps = []  # список кафедр


# класс для кафедры
class Department:
    def __init__(self, name, url):
        self.name = name  # название кафедры
        self.url = url  # url
        self.teachers = []  # список преподавателей


# класс для преподавателя
class Teacher:
    def __init__(self, name, picture=None):
        self.last_name = name.split(' ')[0].strip()  # Фамілія
        self.first_name = name.split(' ')[1].strip()  # Имя
        self.middle_name = name.split(' ')[2].strip()  # Отчество
        self.picture = picture  # url фотки


def create_faculties():
    """создает список инстансов факультетов
    ппарсит гоавную страницу и выбирает из дроп-даун меню
    названия факультетов и их url
    возвращает список инстансов факультетов `Facultet`
    """
    # выделить теги названий факультетов в список
    fac_tags = facs_deps_menu.find_all('span', {'class': 'prev-link'})

    # проход по списку тегов названий и выделение из их
    # родителя (a-тега) названия и url факультета
    # создание инстанса Facultet и заненсенее его в список
    facultets:List[str] = []
    for tag in fac_tags:
        name = tag.parent.find('span').text
        url = tag.parent.get('href')
        facultets += [Facultet(name, url)]

    return facultets


def find_deps(fac_name):
    """ для факультета `fac_name` выбирает из списка тегов tags_a
    входящие в него кафедры по классу `att-menu-item` и
    возвпащает список инстансов кафедр
    """
    deps_list = []
    tags_a = facs_deps_menu.find_all('a')

    # проход по списку тагов `a` из меню факультетов и кафедр
    for i in range(len(tags_a)):
        # если найден факультет `fac_name` то выбираем
        # все следующие таги - кафедры (class:att-menu-item)
        # и сохраняем их в списке deps_list
        if tags_a[i].text == fac_name:
            try:
                while 'att-menu-item' in tags_a[i + 1].get('class'):
                    name = tags_a[i + 1].text
                    url = tags_a[i + 1].get('href')
                    deps_list += [Department(name, url)]
                    i += 1
            except Exception:
                return deps_list


def create_prepods_list(dep_url):
    """
    формирование списка преподавателей по кафедре
    из контента страницы `вікладацькій склад`
    """
    # читаем страницу викладачей в объект bs4 - prep_page
    prep_page = MAIN_PAGE + dep_url
    prep_page = bs(urlopen(prep_page).read().decode('utf-8'), 'html')

    # выделим контент с преподавателями (начнается от div class=post)
    main_part = prep_page.find_all('div', {'class': 'post'})

    # выделим текст (уберем тегі)  и сольем его в список
    text = [x.get_text() for x in main_part]

    # заменіть переноси на `пробел`
    clear_text = ''.join(map(lambda x: ' ' if x == '\n' else x, text[0]))

    # убрать `мусор` (nonprintables)
    clear_text = ''.join(
        map(lambda char: char if char.isprintable() else ' ', clear_text))

    # заменить встречающиеся латинские буквы на кирилицу
    clear_text = lat_to_cyr(clear_text)

    # убрать 2 пробела между словами (бывает в именах преподов)
    clear_text = ' '.join(clear_text.split('  '))

    # форміруем список преподов в верхнем регистре
    prep_names = [x.group().upper() for x in re.finditer(mask, clear_text)]
    # prep_names = [x.group().upper() for x in re.findall(mask, clear_text)]

    #  удалим повторения в списке
    prep_names = list(set(prep_names))

    return prep_names, main_part


def lat_to_cyr(string):
    lat = 'EeTIiOoPpAaHKXxCcBM'
    cyr = 'ЕеТІіОоРрАаНКХхСсВМ'
    trans_tab = string.maketrans(lat, cyr)
    return string.translate(trans_tab)


def create_teachers_object(dep, prepods_list):
    '''
    формирует список преподавателей по кафедре
    вход: dep - инстанс кафедры
          prepods_list - список препоов
    выбирает последовательно имена преподов из prepods_list
    и создает инстанс препода, который добавляется в список
    teachers кафедры
    '''
    for name in prepods_list:
        dep.teachers += [Teacher(name)]


def find_prep_name(last_name, first_name, tags_plain_list):
    """
    проход по преподавателям кафедры и  поиск их фамилии и имени
    в списке тэгов сторинки викладачей кафедры
    возвращает индекс элемента в списке тэгов
    :param last_name:  фио
    :param first_name: имя
    :param tags_plain_list: список тегов страицы преподов
    :return: индекс тега с фио препода
    """
    # паттерн: ФАМИЛИЯ ИМЯ (1-е 3 буквы)
    pat = r'{}\s+{}'.format(last_name, first_name.upper()[:3])

    for index, item in enumerate(tags_plain_list):
        if re.search(pat, lat_to_cyr(item.upper())):
            # фамилия препода д/б в верхнем регистре (как в last_name)
            if last_name in item:
                return index

    return -1  # если фамилия не найдена


def find_img(index):
    """
    Находит 1-й слева и 1-й справа img-теги от фамилии и выбирает ближайший - предполагается,
    что это реальная фотка препода
    :param index:  - индекс фамилии в списке тегов  (tags_plain_list)
    :return: тег img с адресом фотки или None
    """
    left_img_index = right_img_index = None
    # go to first left
    for i in range(index, 0, -1):
        if '<img ' in tags_plain_list[i]:
            left_img_index = i
            break
    # go to first right
    for i in range(index, len(tags_plain_list)):
        if '<img ' in tags_plain_list[i]:
            right_img_index = i
            break

    # проверяем, какой из img-тегов ближе к фамилии (index)
    left_length = index - left_img_index if left_img_index else 99999
    right_length = right_img_index - index if right_img_index else 99999
    if left_length == right_img_index == 99999:
        return None
    if left_length <= right_length:
        return tags_plain_list[left_img_index] + '>'
    if left_length > right_length:
        return tags_plain_list[right_img_index] + '>'


def create_absolute_url(picture):
    """
    # приводит url фотки в абсолютный адрес
    :param picture:
    :return: абсолютный адрес
    """
    # если фотки нету - выход
    if not picture:
        return None

    # если url фотки - уже абсолютный, ничего не делаем и выходим
    if re.match(r'http[s]?://', picture):
        return picture

    # если фотка - blob объект, выбрасываем и выходим
    if 'data:image' in picture:
        return None

    # возвращаем приведенный к абсолютному url фотки
    mask = r'(/file\S+)|(/image\S+)'
    absolute_url = ''
    try:
        absolute_url = re.search(mask, picture).group()
    except AttributeError:
        print('ошибка в url: {}'.format(picture))

    return 'http://knteu.kiev.ua' + absolute_url


if __name__ == '__main__':
    """Parse KNTEU site and extract info and usefull links
    about prepods
    """
    # открыть главную страницу
    main_page = urlopen(MAIN_PAGE).read().decode('utf-8')

    # получить bs-объект
    bs_main_page = bs(main_page, 'html')

    # выделить `body`-контент
    main_page_body = bs_main_page.body

    # выделить контент главного меню
    menues = main_page_body.find_all('ul', {"class": "dropdown-menu"})

    # выделить выпадающее меню `факультеты и кафедры` (2-е)
    facs_deps_menu = menues[1]

    """ основной цикл
        формируем список инстансов факультетов, содержащий списки кафедр
        по каждой кафедре - список инстансов препдов
    """
    # получить список факультеов
    facs_list = create_faculties()

    # формирование списков преподавателей по факультетам-кафедрам
    for fac in facs_list:

        # строим список кафедр факультета `fac`
        # добавляем список кафедр в инстанс факультета
        fac.deps = find_deps(fac.name)
        print(fac.name)

        for dep in fac.deps:
            print('    ' + dep.name)

            # замаскировать non-ASCII в url кафедры и добавить MAIN_PAGE
            # /blog/read?n=Department of Marketing&uk => http://knteu.kiev.ua/blog/read?n=Department%20of%20Marketing&uk
            dep_page = MAIN_PAGE + \
                urllib.parse.quote(dep.url, safe='/blog/read?n=&')

            # получить bs-объект страницы кафедры
            dep_page = bs(urlopen(dep_page).read().decode('utf-8'), 'html')

            # найти а-тег `викладацький склад` или `Склад кафедри` и вытащить
            # из него url страницы преподов
            try:
                url = dep_page.find('a', text=re.compile(
                    '(Викладацький склад|Склад кафедри)')).get('href')
            except AttributeError:
                # страница преподов не найдена - берем след. кафедру
                print('*** страница преподов не найдена')
                continue
            # получаем список преподавателей и сраницу откуда они получены
            prepods_list, main_part = create_prepods_list(url)

            # делаем список тегов страницы
            tags_plain_list = str(main_part[0]).split('>')

            # формируем инстансы преподавателей в классе кафедры
            create_teachers_object(dep, prepods_list)

            # проход по инстансам преподов кафедры - поиск фоток
            for teacher in dep.teachers:
                # находим индекс тега с фамилией
                index = find_prep_name(
                    teacher.last_name, teacher.first_name, tags_plain_list)
                # от index  ищем ссылка на фото
                img_tag = find_img(index)
                if img_tag:
                    # запоминаем ссылку на фото
                    teacher.picture = bs(img_tag, 'html').find('img')['src']
                else:
                    teacher.picture = None

    """
    дописываем  данные из Facs_list в файд time-table.json
    как поле `detail`:...
    """
    # получаем из timetable список ФИО преподов
    with open('time-table.json') as f:
        time_table = json.loads(f.read())

    # список преподов из time-table
    prepod_names_list = list(time_table.keys())

    # на всякий случай уберем латиницу из фамилий
    prepod_names_list = list(map(lambda x: lat_to_cyr(x), prepod_names_list))

    # проход по списку факультетов и заполнение свойства teacher.picture
    # реальным url фотки препода
    print('Подключение фоток\n')
    for fac in facs_list:
        for dep in fac.deps:
            print('--- ', dep.name, dep.url)
            # ищем имя препода в списке преподов из time-table
            for teacher in dep.teachers:
                # готовим поисковое значение из объекта teacher
                searcher = '{} {} {}'.format(teacher.last_name.upper(), teacher.first_name[:1].upper(),
                                             teacher.middle_name[:1].upper())
                for name in prepod_names_list:
                    # если имя препода найдено - добавляем данные препода в time-table
                    if searcher in name.upper():
                        # полное имя препода
                        full_name = '{} {} {}'.format(teacher.last_name.upper(), teacher.first_name.upper(),
                                                      teacher.middle_name.upper())
                        # url фотки
                        url = create_absolute_url(teacher.picture)
                        try:
                            time_table[name]['details'] = {}
                            time_table[name]['details']['img_url'] = url
                            time_table[name]['details']['name'] = full_name
                            time_table[name]['details']['dep'] = dep.name
                            time_table[name]['details']['fac'] = fac.name
                        except KeyError:
                            print('{} - не найден'.format(searcher))

with open('time-table.json', 'w') as f:
    f.write(json.dumps(time_table, indent=2, ensure_ascii=False))
