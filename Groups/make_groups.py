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
from config_app import NAME_OF_WS, CONFIG_JSON

import config_app
import pandas as pd
import json

def main():
    
    # читать config.json
    with open(CONFIG_JSON) as config:
        config_file = json.load(config)
    if not isinstance(config_file, dict):
        print ("Ошибка при чтении config.json")
        exit (1)


if __name__ == "__main__":
    main()