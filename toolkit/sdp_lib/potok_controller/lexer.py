from rply import LexerGenerator


lg = LexerGenerator()

lg.add("L_PAREN", r'\(')
lg.add("R_PAREN", r'\)')
lg.add("PLUS", r"\+")
lg.add("SUB", r'\-')
lg.add("MUL", r'\*')
lg.add('NUM', r'\d+')
lg.add('AND', r'and')
lg.add('OR', r'or')

lg.ignore(r'\s+')


# class Lexer:
#     def __init__(self):
#         self.lexer = LexerGenerator()
#
#     def add_tokens(self):
#         self.lexer.add("L_PAREN", r'\(')
#         self.lexer.add("R_PAREN", r'\)')
#         self.lexer.add("PLUS", r"\+")
#         self.lexer.add("SUB", r'\-')
#         self.lexer.add("MUL", r'\*')
#
#         self.lexer.add('NUM', r'\d+')
#         self.lexer.ignore(r'\s+')
#
#     def get_lexer(self):
#         self.add_tokens()
#         return self.lexer.build()

