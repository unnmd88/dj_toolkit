from rply import ParserGenerator
from rply.token import BaseBox

from ast import Num, Add, Mult, Sub


class Parser:
    TOKENS = (
        "L_PAREN", "R_PAREN",
        "PLUS", "SUB",
        "MUL",
        'NUM'
    )

    def __init__(self):
        self.pg = ParserGenerator(self.TOKENS)

    def parse(self):
        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MUL expression")
        def expression_op(p):
            left = p[0]


TOKENS = (
    "L_PAREN", "R_PAREN",
    "PLUS", "SUB",
    "MUL",
    'NUM'
)

pg = ParserGenerator(
    TOKENS,
    precedence=[
        ("left", ['PLUS', 'MINUS']),
        ("left", ['MUL'])
    ],
    cache_id="myparser"
)

@pg.production("expression : expression PLUS expression")
@pg.production("expression : expression MINUS expression")
@pg.production("expression : expression MUL expression")
def expression_op(p):
    left = p[0].getint
    right = p[2].getint

    if p[1].gettokentype() == "PLUS":
        return BoxInt(left + right)
    elif p[1].gettokentype() == "MINUS":
        return BoxInt(left - right)
    elif p[1].gettokentype() == "MUL":
        return BoxInt(left * right)


class BoxInt(BaseBox):
    def __init__(self, value):
        self.value = value

    def getint(self):
        return self.value


