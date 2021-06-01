
import pytest
from bs4 import BeautifulSoup as bs

from make_config import \
    extract_time_tables, \
    get_time_table_list
    

@pytest.fixture
def soup_page():
    test_html = """
    <html>
        <body>
            <div>
                <strong>ДЕННА ФОРМА НАВЧАННЯ</strong>
            </div>
            <div>БАКАЛАВР</div>
            <table>
                <tbody>
                    <tr><td>ФИТ-бакалавры</td></tr>
                    <tr><td><a href='/file=1 курс'>1 курс</a></td></tr>
                    <tr><td><a href='/file=2 курс'>2 курс</a></td></tr>
                </tbody>
            </table>
            <div>МАГІСТР</div>
            <table>
                <tbody>
                    <tr><td>ФИТ-магистры</td></tr>
                    <tr><td><a href='/file=1 курс'>1 курс</a></td></tr>
                    <tr><td><a href='/file=2 курс'>2 курс</a></td></tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    test_html = test_html.replace('\n','')
    test_html = test_html.replace('  ','')
    soup = bs(test_html, features='html.parser')

    return soup

@pytest.fixture
def soup_table():
    test_html = """
    <table>
        <tbody>
            <tr><td>ФИТ-бакалавры</td></tr>
            <tr><td><a href='/file=1 курс'>1 курс</a></td></tr>
            <tr><td><a href='/file=2 курс'>2 курс</a></td></tr>
        </tbody>
    </table>
    """
    test_html = test_html.replace('\n','')
    test_html = test_html.replace('  ','')
    soup = bs(test_html, features='html.parser')

    return soup

def test_extract_time_tables(soup_page):
    result = extract_time_tables(soup_page)
    assert isinstance(result, tuple) == True
    assert result[0].name == "table"
    assert result[1].name == "table"
    pass

def test_get_time_table_list(soup_table):
    result = get_time_table_list(soup_table)
    assert len(result) > 0 

