import re
import logging
import functools
import time
from typing import Dict

string = "ddr(D4) or ddr(D5) or ddr(D6) or ddr(D7) and mr(G1)" * 10
d1 = {'or': '+', 'and': '*'}
start_time = time.time()

string2 = ''.join((re.sub(c, d1[c], string) for c in d1))
# print(string2)

print(f'время составило: {time.time() - start_time}')


def replace_chars(data: Dict[str, str], string=None) -> str:
    """
    Заменяет символы в строке.
    :param string: строка, в которой требуется заменить символы. если None,
                   то берёт строку self.condition_string_vals_instead_func.
    :param data: k: символы, которые требуется заемить, v: символы, на которые требуется заемить
    :return: строка с заменёнными символами. если kwargs пустой, возвращает переданную строку
    """

    if not data:
        return string
    for pattern, replacement in data.items():
        string = string.replace(pattern, replacement)
    return string

start_time = time.time()
string3 = replace_chars(d1, string)
print(f'время2 составило: {time.time() - start_time}')

print(string3 == string2)

print(string2)
print(string3)