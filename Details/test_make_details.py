from typing import Any, Tuple
from unittest.mock import  patch, Mock
import pytest
import requests

from bs4 import BeautifulSoup as bs  # type: ignore

import make_details
from make_details import Facultet, Department, Teacher
from make_details import  \
    make_fac_list, make_dep_list, \
    make_teacher_list, get_vikl_sklad_href, \
    _extract_teacher_info, get_teacher_key, _find_teacher_name

from constants import MENU, MENU_1_FAC, DEP_PAGE, \
    TEACHER_PAGE, TEACHER_TD, MAZARAKI, TIME_TABLE_EXPECTED, TIME_TABLE_BEFORE, \
    MULTITABLE_TEACHER_PAGE

from config_app import KNTEU_URL


@pytest.fixture
def menu() -> bs:
    return bs(MENU, features='html.parser')


def test_make_fac_list(menu: bs) -> None:
    result = make_fac_list(menu)
    expected = [
        Facultet("Факультет міжнародної торгівлі та права",
                 "/blog/read?n=fmtp&uk"),
        Facultet("Факультет торгівлі\n та маркетингу", "/blog/read?n=ftm&uk"),
        Facultet("Факультет економіки, менеджменту та\n                психології",
                 "/blog/read?n=femp&uk")
    ]
    assert isinstance(result[0], Facultet) == True
    assert result[0].name == expected[0].name and result[0].url == expected[0].url
    assert result[1].name == expected[1].name and result[1].url == expected[1].url
    assert result[2].name == expected[2].name and result[2].url == expected[2].url


@pytest.fixture
def menu_1_fac() -> bs:
    menu = bs(MENU_1_FAC, features='html.parser')
    return menu


def test_make_dep_list(menu_1_fac: bs) -> None:
    fac_name = "Факультет міжнародної торгівлі та права"
    result = make_dep_list(fac_name, menu_1_fac)

    class D(Department):
        def __eq__(self, o: object) -> bool:
            if self.name == o.name and self.url == o.url:  # type: ignore
                return True
            return False

    expected = \
        [D("Кафедра світової економіки", "/blog/read?n=svitovoyi ekonomiki&uk"),
         D("""Кафедра міжнародного
            менеджменту""", "/blog/read?n=Department of International Economics&uk"),
         D("""Кафедра
            філософії, соціології та політології""", "/blog/read?n=Department filosofsmbkikh ta socialmbnikh nauk&uk")
         ]

    assert result == expected


@pytest.fixture
def dep_page() -> bs:
    return bs(DEP_PAGE, features='html.parser')


def test_get_vikl_sklad_page(dep_page: Any) -> None:

    result = get_vikl_sklad_href(dep_page)
    expected = "/blog/read/?pid=41465&uk"
    assert result == expected

    result = get_vikl_sklad_href(bs("<body></body>", features="html.parser"))
    expected = ''
    assert result == expected


# патч на метод `get` модуля 'requests'
@patch.object(requests, 'get')
def test_make_teacher_list(macked_get_resp: Any) -> None:
    """ тестирует построитель списка преподов с страницы кафедры 
    macked_get_resp - патч на 'requests.get'
    
    """
    class T(Teacher):
        def __eq__(self, o: object) -> bool:
            if self.first_name == o.first_name and      \
               self.last_name == o.last_name and        \
               self.middle_name == o.middle_name and    \
               self.picture_url == o.picture_url:       # type: ignore
                return True
            else:
                return False

    expected = [
        T("ДУГІНЕЦЬ ГАННА ВОЛОДИМИРІВНА",
          "/file/Mjk1MQ==/156938c5dc81fcd27209ba38c891adbf.JPG"),
        T("ОНИЩЕНКО ВОЛОДИМИР ПИЛИПОВИЧ",
          "/file/Mjk1MQ==/359babfeb3c26e7a87b9dcb30af37605.jpg"),
        T("КОРЖ МАРИНА ВОЛОДИМИРІВНА",
          "/file/Mjk1MQ==/ccaf86485fe54b5182d890b733020fb9.png"),
        T("ФЕДУН ІГОР ЛЕОНІДОВИЧ", "/file/Mjk1MQ==/a27130a4cf7738a640f5433affd8bd6d.jpg")
    ]
    
    # создать мок респонса 
    mockresponse = Mock()
    # записать в него текст тестовой страницы преподов
    mockresponse.text = TEACHER_PAGE
    # сказать патчу `requests.get` возвращать созданный мок
    macked_get_resp.return_value = mockresponse
    
    # вызвать тестируемую функцию (аргумент не важен)
    result = make_teacher_list('')
        
    assert result[0] == expected[0]
    assert result[1] == expected[1]
    assert result[2] == expected[2]
    assert result[3] == expected[3]
    
    # ТЕСТИРУЕМ МУЛЬТИТАБЛИЧНУЮ СТРАНИЦУ ПРЕПОДОВ

    mockresponse.text = MULTITABLE_TEACHER_PAGE
    macked_get_resp.return_value = mockresponse
    result = make_teacher_list('')


def test_find_teacher_name() -> None:
    teacher_td_tag = bs(TEACHER_TD, 'html')
    result = _find_teacher_name(teacher_td_tag)
    assert result == "ОНИЩЕНКО ВОЛОДИМИР ПИЛИПОВИЧ"
    
    
@pytest.fixture
def teacher_td() -> bs:
    return bs(TEACHER_TD, features="html.parser")


def test_extract_teacher_info(teacher_td: Tuple[str, str]) -> None:
    result = _extract_teacher_info(teacher_td)
    expected = (
        "ОНИЩЕНКО ВОЛОДИМИР ПИЛИПОВИЧ",
        "/file/Mjk1MQ==/359babfeb3c26e7a87b9dcb30af37605.jpg"
    )
    assert result == expected


@pytest.fixture
def mazaraki_td() -> bs:
    return bs(MAZARAKI, features="html.parser")


def test_mazaraki(mazaraki_td: bs) -> None:
    result = _extract_teacher_info(mazaraki_td)
    expected = (
        '',
        "/image/ODM1OA==/3a25ff19b7b81ca9c2d7ceec5ff55302.jpg"
    )
    assert result == expected

def test_get_teacher_key() -> None:
    expected = "доц Котляр В Ю "
    result = get_teacher_key("Котляр В Ю", TIME_TABLE_EXPECTED)
    assert expected == result
    expected = ''
    result = get_teacher_key("доц ПУПКИН", TIME_TABLE_EXPECTED)
    assert expected == result
    expected = "проф П'ятницька Г Т "
    result = get_teacher_key("П'ятницька Г Т", TIME_TABLE_EXPECTED)
    assert expected == result
