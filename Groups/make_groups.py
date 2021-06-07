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
from config_app import NAME_OF_WS, CONFIG_JSON, KNTEU_URL, WEEK_NOMER, GROUP, DAY_NAME

from pandas.core.frame import DataFrame
import pandas as pd
import json
from typing import Any
import re

def make_groups_list(href: str) -> list[str]:
    """ по href чытает excel в датафрейм
    вызывает 
        - построитель списка листов с реальным расписанием
        - для выбранных листов вызывает постоитель списка групп
    возвращает список групп
    """
        
    # прочитать xls в словарь датафреймов
    url = KNTEU_URL + href
    time_tables_dict:dict[str, Any] = pd.read_excel(url, sheet_name=None, header=None)
    
    # построить список листов с актуальным расписанием
    sheet_names_list:list[str] = get_sheet_names(time_tables_dict)
    
    # для каждого актуального листа выбрать в group_list группы
    group_list: list[str] = []
    for sheet_name in sheet_names_list:
        group_list += get_group_list(time_tables_dict[sheet_name])
        
    # пропустить group_list через set для устранения дублей
    group_list = list(set(group_list))
    
    return group_list

def get_group_list(time_table: DataFrame) -> list[str]:
    """ принимает датафрейм, ищет в нем строку с паттерном GRUPA
    если найден, то проходит по этой строке и выбирает все номера групп
    возвращает список номеров групп
    """
    
    group_list: list[str] = []
    for _, row in time_table.iterrows():
        # if GROUP in ''.join([x for x in list(row) if type(x) == str]):
        if re.search(GROUP, ''.join([x for x in list(row) if type(x) == str])):
            group_list += [x.split()[0] for x in list(row) if x and GROUP in x]

    return group_list

def get_sheet_names(dfs:dict[str, Any]) -> list[str]:
    """ принимает славарь датафреймов
    для каждого датафрейма ищет паттерн WEEK_NOMER ('Номер????тижня')
    ято является признаком реального расписания и  добавляет название
    этого дадафрейма в список листов с расписанием
    """
    
    output = []
    sheet_names = dfs.keys()
    for name in sheet_names:
        for _, row in dfs[name].iterrows():
            if any ([lambda x: re.match(WEEK_NOMER, x) for x in list(row) if x is not None]):
                output.append(name)
                
    return output

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
            groups[fac][course_number + 1] = make_groups_list(course_href)
            print (f'{course_number + 1} курс : {groups[fac][course_number + 1]}')

        print('\n')
            
        


if __name__ == "__main__":
    main()