import pytest
import pandas as pd
from make_groups import get_groups_list, get_sheet_names

def test_get_sheet_names():
    result = get_sheet_names(["Розклад", "Лист", "1-10 гр.розклад", "Начитка"])
    assert result == ["Розклад", "1-10 гр.розклад"]
    result = get_sheet_names([])
    assert result == []
    result = get_sheet_names(["Лист"])
    assert result == []
    result = get_sheet_names(["Розклад 5-14,23гр "])
    assert result == ["Розклад 5-14,23гр "]
    