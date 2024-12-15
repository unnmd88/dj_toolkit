from language.lexer import lg
from language.parser import pg


class ConditionResult:
    def __init__(self, condition_data: str):
        self.condition_data = condition_data
        self.current_result = None

    def __repr__(self):
        return f'Строка: {self.condition_data}\nПоследний полученный результат: {self.current_result}'

    def get_condition_result(self) -> bool:
        lexer = lg.build()
        parser = pg.build()

        result: int = parser.parse(lexer.lex(self.condition_data))
        self.current_result = bool(result)
        print(f'int result: {result}, bool result: {self.current_result}')
        return self.current_result


if __name__ == '__main__':
    t = ConditionResult('(1 or 0 or 1 or 0 or 0 or 0 or 1 or 0 '
    'or 1 or 1 or 0 and 1) and 1'
    ' and 0 and 1 or 0')
    print(t.get_condition_result())
    print(t)
