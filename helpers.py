"""часто используемые функции
"""


def clean_string(string: str) -> str:
    """ удаляет из строки `sring` повторяющиеся пробелы и \n """

    string = string.replace('\n', ' ')
    string = ' '.join(string.split())

    return string


def lat_to_cyr(string: str):
    """замещает латиницу кирилицей
    """
    lat = 'EeTIiOoPpAaHKXxCcBM'
    cyr = 'ЕеТІіОоРрАаНКХхСсВМ'
    trans_tab = string.maketrans(lat, cyr)
    return string.translate(trans_tab)


def fix_apostroph(word: str) -> str:
    """заменяет вордовский апостроф на `'`
    """
    return word.replace("’", "'")

def complex_name(word: str) -> str:
    """в фамилии типа 'Петренко-иванов' капіталізірует 2-ю часть
    """
    if word == None:
        return word
    
    if '-' in word:
        s = word.split('-')
        return f"{s[0]}-{s[1].capitalize()}"
    
    return word