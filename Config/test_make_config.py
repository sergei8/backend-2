
# import pytest
from make_config import \
    get_timetable_page

def test_get_timetable_page():
    assert get_timetable_page() != None
    assert get_timetable_page().status_code == 200

# def test_get_parsed_timetable():
#     pass