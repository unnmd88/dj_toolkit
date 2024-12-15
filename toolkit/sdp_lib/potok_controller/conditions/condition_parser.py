import re
import logging
from typing import List


class ConditionParser:
    def __init__(self, condition_string: str):
        self.condition_string = condition_string
        self.tokens = None

    def create_tokens(self) -> List:
        tokens = []
        data = self.condition_string.split()

        for i, fragment in enumerate(data):
            if 'ddr' in fragment:
                f_name = 'ddr'
                arg = 'D'
                token = self.add_token(f_name, fragment, arg)
            elif 'ddo' in fragment:
                f_name = 'ddr'
                arg = 'D'
                token = self.add_token(f_name, fragment, arg)
            elif 'mr' in fragment:
                f_name = 'mr'
                if 'G' in fragment:
                    arg = 'G'
                elif 'A' in fragment:
                    arg = 'A'
                else:
                    raise ValueError('Неверный аргумент функции mr')
                token = self.add_token(f_name, fragment, arg)
            elif 'fctmg' in fragment:
                f_name = 'fctmg'
                arg = 'G'
                token = f'{self.add_token(f_name, fragment, arg)} {data.pop(i + 1)} {data.pop(i + 1)}'
            else:
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
            'fctmg': r'[1-9]{1,2}'
        }

        pattern = patterns_regexp.get(f_name)
        digit_argument = re.findall(pattern, fragment)
        if len(digit_argument) > 1 or int(digit_argument[0]) > 128:
            raise ValueError('Неверный аргумент функции')
        return f'{f_name}({name_argument}{digit_argument[0]})'


string = (
    '(ddr(D33) or ddr(D34) or ddr(D35) or ddr(D36) or ddr(D37) or ddr(D38) or ddr(D39) or ddr(D40) '
    'or ddr(D41) or ddr(D42) or ddr(D43) or ddr(D44) or ddr(D45) or ddr(D46) or ddr(D47)) and mr(G1)'
    ' and fctmg(G1) >= 40 and ddr(D1) or not ddr(D120)')

manager = ConditionParser(string)

res = manager.create_tokens()
print(res)

# for tok in res_parse:
#     string = string.replace(tok, 'False').replace('and', '*').replace()



