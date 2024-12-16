import re
from typing import List

from .constants import DET_FUNCTIONS, ALLOWED_FUNCTIONS, SG_FUNCTIONS

class ConditionParser:
    """
    Класс - обрабчик в строки условия перехода/продления
    Traffic lights configurator контроллера Поток
    """

    def __init__(self, condition_string: str):
        """
        :param condition_string: Строка с условием перехода/продления
                                 Traffic lights configurator контроллера Поток
        """

        self.condition_string = condition_string
        self.tokens = None

    # def create_tokens(self) -> List:
    #     """
    #     Формирует список токенов(функций) из self.condition_string
    #     :return: Список токенов(функций из self.condition_string)
    #     """
    #
    #     tokens = []
    #     data = self.condition_string.split()
    #
    #     for i, fragment in enumerate(data):
    #         if 'ddr' in fragment:
    #             f_name = 'ddr'
    #             arg = 'D'
    #             token = self.add_token(f_name, fragment, arg)
    #         elif 'ddo' in fragment:
    #             f_name = 'ddo'
    #             arg = 'D'
    #             token = self.add_token(f_name, fragment, arg)
    #         elif 'mr' in fragment:
    #             f_name = 'mr'
    #             if 'G' in fragment:
    #                 arg = 'G'
    #             elif 'A' in fragment:
    #                 arg = 'A'
    #             else:
    #                 raise ValueError('Неверный аргумент функции mr')
    #             token = self.add_token(f_name, fragment, arg)
    #         elif 'fctg' in fragment:
    #             f_name = 'fctg'
    #             arg = 'G'
    #             token = f'{self.add_token(f_name, fragment, arg)} {data.pop(i + 1)} {data.pop(i + 1)}'
    #         else:
    #             continue
    #
    #         if i > 0 and 'not' in data[i - 1]:
    #             token = f'not {token}'
    #
    #         tokens.append(token)
    #     self.tokens = tokens
    #     print(f'self.token')
    #     return tokens

    def create_tokens(self) -> List:
        """
        Формирует список токенов(функций) из self.condition_string
        :return: Список токенов(функций) из self.condition_string
        """

        tokens = []
        data = self.condition_string.split()

        for i, fragment in enumerate(data):
            token = None
            for f_name in ALLOWED_FUNCTIONS:
                if f_name in fragment:
                    arg = self._get_arg(f_name, fragment)
                    if f_name == 'fctg':
                        token = f'{self.add_token(f_name, fragment, arg)} {data.pop(i + 1)} {data.pop(i + 1)}'
                    else:
                        token = self.add_token(f_name, fragment, arg)
                    break
            if token is None:
                continue

            if i > 0 and 'not' in data[i - 1]:
                token = f'not {token}'

            tokens.append(token)
        self.tokens = tokens
        return tokens

    def add_token(self, f_name: str, fragment: str, name_argument: str):
        patterns_regexp = {
            'ddr': r'[0-9]{1,3}',
            'ddo': r'[0-9]{1,3}',
            'ngp': r'[0-9]{1,3}',
            'mr': r'[1-9]{1,2}',
            'fctg': r'[1-9]{1,2}'
        }

        pattern = patterns_regexp.get(f_name)
        digit_argument = re.findall(pattern, fragment)
        if len(digit_argument) > 1 or int(digit_argument[0]) > 128:
            raise ValueError('Неверный аргумент функции')
        return f'{f_name}({name_argument}{digit_argument[0]})'

    def _get_arg(self, f_name: str, fragment: str):
        """
        Определяет часть аргумента для переданной функции.
        :param f_name: имя токена-функции контроллера Поток: 'ddr', 'mr', 'fctg' и т.д.
        :param fragment: Фрагмент, в котором осуществляется поиск(элемент списка, получившегося после
                         функции split() на строке условии вызова/продления.
                         Например: '((ddr(D25)', 'ddr(D5)', 'mr(G1)', 'and' и т.д.
        :return: аргумент для функции: D(для функии дет), G или A для функции sg
        """

        if f_name in DET_FUNCTIONS:
            if 'D' not in fragment:
                raise ValueError(f'Неверный аргумент одной из фунций {f_name}')
            arg = 'D'
        elif f_name in SG_FUNCTIONS:
            if 'G' in fragment:
                arg = 'G'
            elif 'A' in fragment:
                arg = 'A'
            else:
                raise ValueError(f'Неверный аргумент одной из фунций {f_name}')
        else:
            raise TypeError(f'Передана некорректная функция {f_name}')
        return arg



string = (
    '(ddr(D33) or ddr(D34) or ddr(D35) or ddr(D36) or ddr(D37) or ddr(D38) or ddr(D39) or ddr(D40) '
    'or ddr(D41) or ddr(D42) or ddr(D43) or ddr(D44) or ddr(D45) or ddr(D46) or ddr(D47)) and mr(G1)'
    ' and fctg(G1) >= 40 and ddr(D1) or not ddr(D120)')



if __name__ == '__main__':
    manager = ConditionParser(string)

    res = manager.create_tokens()
    print(res)
    # for tok in res_parse:
    #     string = string.replace(tok, 'False').replace('and', '*').replace()



