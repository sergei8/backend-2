"""часто используемые функции
"""


def clean_string(string: str) -> str:
    """ удаляет из строки `sring` повторяющиеся пробелы и \n """

    string = string.replace('\n', ' ')
    string = ' '.join(string.split())

    return string

def lat_to_cyr(string:str):
    """замещает латиницу кирилицей
    """
    lat = 'EeTIiOoPpAaHKXxCcBM'
    cyr = 'ЕеТІіОоРрАаНКХхСсВМ'
    trans_tab = string.maketrans(lat, cyr)
    return string.translate(trans_tab)
