"""
выбирает из excel-таблиц с расписанием номера групп
и формирует json вида:
        {
            <фак-т> : {
                <курс>: [номера групп]
            }
        }
"""

import sys
sys.path.insert(0,'.')
from config_app import NAME_OF_WS, CONFIG_JSON, KNTEU_URL, \
    WEEK_NOMER, GROUP, DAY_NAME, GROUPS_JSON

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
        group_list += get_group_list(sheet_name, time_tables_dict[sheet_name])
        
    # пропустить group_list через set для устранения дублей
    group_list = list(set(group_list))
    
    return sorted(group_list)

def get_group_list(sheet_name: str, time_table: DataFrame) -> list[str]:
    """ принимает датафрейм и имя excel-листа, ищет в нем строку с паттерном GRUPA
    если найден, то проходит по этой строке и выбирает все номера групп
    возвращает список номеров групп
    """
    
    for _, row in time_table.iterrows():
        try:
            if re.search(GROUP, ''.join([x for x in list(row) if type(x) == str])):
                return [x.split()[0] for x in list(row) if not pd.isna(x) and GROUP in x]
        except:
                print(f"ошибка парсинга [{sheet_name}] : get_group_list")
                continue
        
    return []

def get_sheet_names(dfs:dict[str, Any]) -> list[str]:
    """ принимает славарь датафреймов
    для каждого датафрейма ищет паттерн WEEK_NOMER (см. config_app)
    что является признаком реального расписания и  добавляет название
    этого дадафрейма в список листов с расписанием
    """
    
    output:list[str] = []
    sheet_names = dfs.keys()
    for name in sheet_names:
        for _, row_as_serial in dfs[name].iterrows():
            try:
                if any([x for x in row_as_serial.str.match(WEEK_NOMER) if not pd.isna(x)]):
                    output.append(name)
                    break
            except:
                print(f"ошибка парсинга [{name}] : get_sheet_names")
                continue
    return output


def main():
    
    # читать config.json
    with open(CONFIG_JSON) as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        print ("Ошибка при чтении config.json")
        exit (1)
    
    # цикл прохода по config_file и формирование выходного json
    groups: dict[str, dict[str, list[str]]] = {}
    for fac in config:
        print(fac)
        groups[fac] = {}
        # проход по списку href расписаний 
        for (course_number, course_href) in enumerate(config[fac]):
            groups[fac][course_number + 1] = make_groups_list(course_href)
            print (f'{course_number + 1} курс : {groups[fac][course_number + 1]}')

        print('\n')
            
    # писать выходной json
    with open(GROUPS_JSON, 'w') as groups_file:
        json.dump(groups, groups_file,ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()