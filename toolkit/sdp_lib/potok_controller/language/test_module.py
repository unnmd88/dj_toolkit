import re
import logging


def replace_bracket(data):
    tokens = []
    print(len(data))
    for i, fragment in enumerate(data):
        if 'ddr' in fragment:
            f_name = 'ddr'
            arg = 'D'
            token = create_token(f_name, fragment, arg)
            # tokens.append(create_token(f_name, fragment, arg))
        elif 'ddo' in fragment:
            f_name = 'ddr'
            arg = 'D'
            token = create_token(f_name, fragment, arg)
            # tokens.append(create_token(f_name, fragment, arg))
        elif 'mr' in fragment:
            f_name = 'mr'
            if 'G' in fragment:
                arg = 'G'
            elif 'A' in fragment:
                arg = 'A'
            else:
                raise ValueError('Неверный аргумент функции mr')
            token = create_token(f_name, fragment, arg)
            # tokens.append(create_token(f_name, fragment, arg))
        elif 'fctmg' in fragment:
            f_name = 'fctmg'
            arg = 'G'
            token = f'{create_token(f_name, fragment, arg)} {data.pop(i + 1)} {data.pop(i + 1)}'
            # tokens.append(f'{create_token(f_name, fragment, arg)} {data.pop(i + 1)} {data.pop(i + 1)}')
        else:
            continue

        try:
            if i > 0 and 'not' in data[i - 1]:
                token = f'not {token}'
        except IndexError as err:
            print(f'i: {i}')

        tokens.append(token)

    print(tokens)
    return tokens


def create_token(f_name, fragment, name_argument):

    patterns_regexp = {
        'ddr': r'[0-9]{1,3}',
        'ddo': r'[0-9]{1,3}',
        'ngp': r'[0-9]{1,3}',
        'mr': r'[1-9]{1,2}',
        'fctmg': r'[1-9]{1,2}'
    }

    pattern = patterns_regexp.get(f_name)
    digit_argument = re.findall(pattern, fragment)
    if len(digit_argument) > 1:
        raise ValueError('Неверный аргумент функции')
    # print(f'{f_name}({name_argument}{digit_argument[0]})')
    return f'{f_name}({name_argument}{digit_argument[0]})'


string = (
    '(ddr(D33) or ddr(D34) or ddr(D35) or ddr(D36) or ddr(D37) or ddr(D38) or ddr(D39) or ddr(D40) '
    'or ddr(D41) or ddr(D42) or ddr(D43) or ddr(D44) or ddr(D45) or ddr(D46) or ddr(D47)) and mr(G1)'
    ' and fctmg(G1) >= 40 and ddr(D1) or not ddr(D120)')

print(string.split())
print(string)
print('_------------------------')
res_parse = replace_bracket(string.split())
print(res_parse)
for tok in res_parse:
    string = string.replace(tok, 'False').replace('and', '*').replace()
print(string)
print(eval(string))

logger = logging.getLogger(__name__)
string = '(ddr(D333)'
# string = string.split()

print(re.findall(r'[1-9]{1,3}', '(ddr(D33333))'))
