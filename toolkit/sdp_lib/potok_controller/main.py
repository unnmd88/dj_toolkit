from lexer import Lexer

txt = "2 + 2 * (2 + 4)"
lexer = Lexer().get_lexer()


for token in lexer.lex(txt):
    print(token)