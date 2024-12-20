import re
from typing import List, Dict
from .lexer import LexerOriginalConditionString


lexer = LexerOriginalConditionString.get_lexer().build()


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

        self.tokens = [token.value.strip() for token in lexer.lex(self.condition_string)]
        print(self.tokens)
        return self.tokens


