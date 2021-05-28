
import pytest
from bs4 import BeautifulSoup as bs
# from re import sub

# import sys
# sys.path.append('./Config')

from make_config import \
    extract_time_tables
    

@pytest.fixture
def soup_page():
    test_html = """
    <html>
        <body>
            <div>
                <strong>ДЕННА ФОРМА НАВЧАННЯ</strong>
            </div>
            <div>...</div>
            <table>
                <tbody>
                    <tr><td>ФИТ-бакалавры</td></tr>
                    <tr><td><a href='/file=бакалавры'>...</a></td></tr>
                </tbody>
            </table>
            <div>...</div>
            <table>
                <tbody>
                    <tr><td>ФИТ-магистры</td></tr>
                    <tr><td><a href='/file=магистры'>...</a></td></tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    test_html = test_html.replace('\n','')
    test_html = test_html.replace('  ','')
    soup = bs(test_html, features='html.parser')

    return soup

def test_extract_time_tables(soup_page):
    assert isinstance(extract_time_tables(soup_page), tuple) == True
    pass