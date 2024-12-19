from rply import LexerGenerator


lg = LexerGenerator()

lg.add("L_PAREN", r'\(')
lg.add("R_PAREN", r'\)')
lg.add("PLUS", r"\+")
lg.add("MUL", r'\*')
lg.add('NUM', r'\d+')

lg.ignore(r'\s+')



