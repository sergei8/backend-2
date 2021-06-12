"""часто используемые функции
"""


def clean_string(string: str) -> str:
    """ удаляет из строки `sring` повторяющиеся пробелы и \n """

    string = string.replace('\n', ' ')
    string = ' '.join(string.split())

    return string
