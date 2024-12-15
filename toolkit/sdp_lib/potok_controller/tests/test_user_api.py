from unittest import TestCase, main
from toolkit.sdp_lib.potok_controller import user_api

class TestGetTokens(TestCase):

    def test_get_tokens(self):
        string_condition = '(ddr(D21) ddr(D22) or ddr(D23) or ddr(D24) or ddr(D30)) and mr(G6)'
        tokens = user_api.Tokens(string_condition).get_tokens()
        self.assertEqual(tokens, ['ddr(D21)', 'ddr(D22)', 'ddr(D23)', 'ddr(D24)', 'ddr(D30)', 'mr(G6)'])


if __name__ == '__main__':
    main()

