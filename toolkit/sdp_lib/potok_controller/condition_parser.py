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
                    token = self.add_token(f_name, fragment, arg)
                    if f_name == 'fctg':
                        token = self._validate_fctg(token, data.pop(i + 1), data.pop(i + 1))
                    break
            if token is None:
                continue

            if i > 0 and 'not' in data[i - 1]:
                token = f'not {token}'

            tokens.append(token)
        self.tokens = tokens
        return tokens

    def _validate_fctg(self, token: str, operator: str, value: str) -> str:
        """
        Проверяет валидность оператора и значения для функции fctg.
        :param token: fctg по дефолту
        :param operator: оператор из функции условия вызова/продления
        :param value: значение из функции условия вызова/продления
        :return: Токен(функция). Пример: 'fctg(G1) >= 40'
        """

        if operator not in {'>', '<', '==', '>=', '<='}:
            raise TypeError(f'Недопустимый оператор для функции fctg: {operator}')
        if not value.isdigit() or value.startswith('0'):
            raise ValueError(f'Недопустимое значение функции fctg: {value}')
        return f'{token} {operator} {value}'

    def add_token(self, f_name: str, fragment: str, name_argument: str) -> str:
        """
        Генерирует токен(функцию)
        :param f_name: имя функции: 'ddr', 'mr', 'fctg' и т.д.
        :param fragment: элемент списка, из строки self.condition_string.split()
                         '(((ddr(D1)', '(ddr(D2))', 'ddr(D3)', 'fctg >= 40' и т.д.
        :param name_argument: Символ аргумента в зависимости от типа функции:
                              D если ddr, G или A если mr и т.д.
        :return: Токен(функция) вида: 'ddr(D22)', fctg(G1), 'ngp(D21)' и т.д.
        """

        patterns_regexp = {
            'ddr': r'[0-9]{1,3}',
            'ddo': r'[0-9]{1,3}',
            'ngp': r'[0-9]{1,3}',
            'mr': r'[0-9]{1,3}',
            'dr': r'[0-9]{1,3}',
            'fctg': r'[0-9]{1,3}'
        }

        pattern = patterns_regexp.get(f_name)
        digit_argument = re.findall(pattern, fragment)
        if len(digit_argument) > 1 or int(digit_argument[0]) > 128 or digit_argument[0].startswith('0'):
            raise ValueError(f'Неверный аргумент функции {f_name}: {"".join(digit_argument)}')
        return f'{f_name}({name_argument}{digit_argument[0]})'

    def _get_arg(self, f_name: str, fragment: str) -> str:
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
