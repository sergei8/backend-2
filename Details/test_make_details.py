import pytest

from bs4 import BeautifulSoup as bs
from make_details import Facultet, Department
from make_details import make_fac_list, make_dep_list

import sys
sys.path.insert(0, '.')
from constants import MENU, MENU_1_FAC


@pytest.fixture
def menu():
    return bs(MENU, features='html.parser')


def test_make_fac_list(menu):
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
def menu_1_fac():
    menu = bs(MENU_1_FAC, features='html.parser')
    return menu


def test_make_dep_list(menu_1_fac):
    fac_name = "Факультет міжнародної торгівлі та права"
    result = make_dep_list(fac_name, menu_1_fac)

    class D(Department):
        def __eq__(self, o: object) -> bool:
            if self.name == o.name and self.url == o.url:
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
