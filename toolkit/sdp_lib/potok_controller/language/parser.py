from rply import ParserGenerator
from rply.token import BaseBox

from lexer import lg

TOKENS = (
    "L_PAREN",
    "R_PAREN",
    "PLUS",
    "SUB",
    "MUL",
    'NUM'
)

pg = ParserGenerator(
    TOKENS,
    precedence=[
        ("left", ['PLUS', 'SUB']),
        ("left", ['MUL'])
    ]
)


# class Parser:
#     TOKENS = (
#         "L_PAREN", "R_PAREN",
#         "PLUS", "SUB",
#         "MUL",
#         'NUM'
#     )
#
#     def __init__(self):
#         self.pg = ParserGenerator(self.TOKENS)
#
#
#     @pg.production("expression : expression PLUS expression")
#     @pg.production("expression : expression MUL expression")
#     def expression_op(self, p):
#         left = p[0]
#         op = p[1]
#         right = p[2]
#
#         if op.gettokentype() == "PLUS":
#             return left + right
#         elif op.gettokentype() == "SUB":
#             return left - right
#         elif op.gettokentype() == "MUL":
#             return left * right
#
#     @pg.production("expression : NUM")
#     def expression_num(self, p):
#         return int(p[0].value)
#
#     @pg.production("expression : L_PAREN expression R_PAREN")
#     def expression_br(self, p):
#         return p[1]


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
lexer = lg.build()

for token in lexer.lex(txt):
    print(token)

parser = pg.build()

print(parser.parse(lexer.lex(txt)))



