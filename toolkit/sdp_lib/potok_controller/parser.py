from rply import ParserGenerator
from rply.token import BaseBox

from lexer import Lexer




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
    'NUM',

)

pg = ParserGenerator(
    TOKENS,
    precedence=[
        ("left", ['PLUS', 'SUB']),
        ("left", ['MUL'])
    ],
    cache_id="myparser"
)


# @pg.production("main : expression")
# def main(p):
#     # p is a list, of each of the pieces on the right hand side of the
#     # grammar rule
#     print(p[0])
#     return p[0]

@pg.production("expression : NUM")
def expression_num(p):
    return int(p[0].value)


@pg.production("expression : L_PAREN expression R_PAREN")
def expression_br(p):
    return p[1]


@pg.production("expression : expression PLUS expression")
@pg.production("expression : expression SUB expression")
@pg.production("expression : expression MUL expression")
def expression_op(p):
    left = p[0]
    op = p[1]
    right = p[2]

    if op.gettokentype() == "PLUS":
        return left + right
    elif op.gettokentype() == "SUB":
        return left - right
    elif op.gettokentype() == "MUL":
        return left * right



txt = "(3 + 3*(2 + 4*(2+15))  * 3) * 2"
# txt = "3 + 3* (2 + 4) + 2"
lexer = Lexer().get_lexer()

for token in lexer.lex(txt):
    print(token)


parser = pg.build()

print(parser.parse(lexer.lex(txt)))

