import pytest
import pandas as pd
import numpy as np
from make_groups import get_sheet_names, get_group_list

@pytest.fixture
def dfs():
    d_dfs = \
    {
        "Розклад" : pd.DataFrame(
            [
                [None, None, None, None],
                ["Номер\nтижня", "День\nтижня", "Пара\n", None],
                [None, None, None, None]
             ]
        ),
        "Начитка" : pd.DataFrame(
            [
                [None, None, None, None],
                [None, None, None, None]
             ]
        ),
        "з 08.02 Розклад" : pd.DataFrame(
            [
                [None, None, None, None],
                ["Номер   тижня", "День\nтижня", "Пара\n", None],
                [None, None, None, None]
             ]
        )
    }
    
    return d_dfs    
def test_get_sheet_names(dfs):
    result = get_sheet_names(dfs)
    assert result == ["Розклад", "з 08.02 Розклад"]
    result = get_sheet_names({"Лист": pd.DataFrame([])})
    assert result == []

@pytest.fixture
def time_table():
    df = pd.DataFrame(
        [
            [None, None, None, None, None],
            ["Номер\nтижня", "День\nтижня", "Пара\n", "Online", None],
            [None, None, None, None],
            ["Номер\nтижня", "День\nтижня", "Пара\n", "1 група", "2 група"],
            [None, None, None, None, None]
        ]
    )
    return df
def test_get_group_list(time_table):
    expected = ["1", "2"]
    result = get_group_list(time_table)
    assert expected == result
    result = get_group_list(pd.DataFrame([]))
    assert result == []
