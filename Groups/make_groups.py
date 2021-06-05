"""
выбирает из excel-таблиц с расписанием номера групп
и формирует json вида:
        {
            <фак-т> : {
                <курс>: [номера групп]
            }
        }
"""
# mypy: ignore_missing_imports = True

import sys
sys.path.insert(0,'.')
from config_app import NAME_OF_WS, CONFIG_JSON, KNTEU_URL

from pandas.core.frame import DataFrame
import pandas as pd
import json
from typing import Any


def get_groups_list(href: str) -> list[str]:
    
    group_list: list[str] = []
    
    # прочитать xls в словарь датафреймов
    url = KNTEU_URL + href
    time_tables_dict:dict[str, Any] = pd.read_excel(url, sheet_name=None, header=None)
    
    # построить список листов с актуальным расписанием
    sheet_names_list:list[str] = list(time_tables_dict.keys())
    sheet_names_list = get_sheet_names(sheet_names_list)
    
    # для каждого актуального листа выбрать в group_list группы
    
    # пропустить group_list через set для устранения дублей
    group_list = list(set(group_list))
    
    return group_list

def get_sheet_names(names:list[str]) -> list[str]:
    
    return [name for name in names 
            if len(list(filter(lambda x: x in name.lower().strip(), NAME_OF_WS))) > 0]


def main():
    
    # читать config.json
    with open(CONFIG_JSON) as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        print ("Ошибка при чтении config.json")
        exit (1)
    
    groups: dict[str, dict[str, list[str]]] = {}
    # цикл прохода по config_file и формирование выходного json
    for fac in config:
        print(fac)
        groups[fac] = {}
        # проход по списку href расписаний 
        for (course_number, course_href) in enumerate(config[fac]):
            groups[fac][course_number + 1] = get_groups_list(course_href)
            print (f'{course_number + 1} курс : {[]}')

        print('\n')
        pass      
            
        


if __name__ == "__main__":
    main()