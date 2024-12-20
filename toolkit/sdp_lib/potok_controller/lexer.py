from rply import LexerGenerator


lg = LexerGenerator()

lg.add("L_PAREN", r'\(')
lg.add("R_PAREN", r'\)')
lg.add("PLUS", r"\+")
lg.add("MUL", r'\*')
lg.add('NUM', r'\d+')
lg.add('NOT', r'not')

lg.ignore(r'\s+')


class LexerOriginalConditionString:
    @classmethod
    def get_lexer(cls):
        lg_ = LexerGenerator()
        lg_.add("ddr", r'ddr\(D\d{1,3}\)')
        lg_.add("ddo", r'ddo\(D\d{1,3}\)')
        lg_.add("ngp", r'ngp\(D\d{1,3}\)')
        lg_.add("fctg", r'fctg\(G\d+\)\s*([<>]=?|==)\s*(\d+)')
        lg_.add('mr', r'mr\(G\d{1,3}\)')
        lg_.ignore(r'not|or|and|[\s+\(\)]')
        return lg_



