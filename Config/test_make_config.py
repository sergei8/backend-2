import pytest
from bs4 import BeautifulSoup as bs

from make_config import \
    extract_time_tables, \
    get_time_table_list, \
    make_output_json_keys, \
    make_output_json_values, \
    make_final_json
    

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

def test_extract_time_tables(soup_page):
    result = extract_time_tables(soup_page)
    assert isinstance(result, tuple) == True
    assert result[0].name == "table"
    assert result[1].name == "table"
    pass

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
def test_get_time_table_list(soup_table):
    result = get_time_table_list(soup_table)
    assert len(result) > 0 

@pytest.fixture
def soup_table_0_row():
    test_html = """<tr><td>ФИТ</td><td>ФЕМП</td><td>ФМТП</td></tr>"""
    test_html = test_html.replace('\n','')
    test_html = test_html.replace('  ','')
    soup = bs(test_html, features='html.parser')

    return soup
def test_make_output_json_keys(soup_table_0_row):
    result = make_output_json_keys(soup_table_0_row)
    assert isinstance(result, dict) == True
    assert result == {
        "ФИТ": None,
        "ФЕМП":None,
        "ФМТП":None
    }


@pytest.fixture
def soup_table_values():
    test_html = ["""
            <tr><td><a href='/file=aaa1.xlsx'>1 курс</a></td>
            <td><a href='/file=bbb1.xlsx'>1 курс</a></td></tr>
    """,
    """
            <tr><td><a href='/file=aaa2.xlsx'>2 курс</a></td>
            <td><a href='/file=bbb2.xlsx'>2 курс</a></td></tr>
    """,
    """
            <tr><td><a href='/file=aaa3.xlsx'>3 курс</a></td>
            <td><a href='/file=bbb3.xlsx'>3 курс</a></td></tr>
    """]
    
    soup = []
    for i in range(3):
        test_html[i] = test_html[i].replace('\n','')
        test_html[i] = test_html[i].replace('  ','')
        soup.append(bs(test_html[i], features='html.parser'))
        
    return soup

def test_make_output_json_values(soup_table_values):
    result = make_output_json_values(soup_table_values)
    assert result == [
        ['/file=aaa1.xlsx', "/file=bbb1.xlsx"],
        ['/file=aaa2.xlsx', "/file=bbb2.xlsx"],
        ['/file=aaa3.xlsx', "/file=bbb3.xlsx"]
    ]
    
def test_make_final_json():
    keys = ["ФИТ", "ФЕМП", "ФМТП"]
    values = [
        ['/file=aaa1.xlsx', "/file=bbb1.xlsx", "/file=ccc1.xlsx"],
        ['/file=aaa2.xlsx', "/file=bbb2.xlsx", "/file=ccc2.xlsx"],
        ['/file=aaa3.xlsx', "/file=bbb3.xlsx", "/file=ccc3.xlsx"]
    ]
    result = make_final_json(keys, values)
    assert isinstance(result, dict) == True
    assert len(result.keys()) == 3
    assert result == {
        "ФИТ"  : ['/file=aaa1.xlsx', '/file=aaa2.xlsx', '/file=aaa3.xlsx'],
        "ФЕМП" : ['/file=bbb1.xlsx', '/file=bbb2.xlsx', '/file=bbb3.xlsx'],
        "ФМТП" : ['/file=ccc1.xlsx', '/file=ccc2.xlsx', '/file=ccc3.xlsx']
    }