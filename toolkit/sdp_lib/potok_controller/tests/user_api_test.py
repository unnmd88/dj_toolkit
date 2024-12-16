from random import randint
from unittest import TestCase, main
from toolkit.sdp_lib.potok_controller import user_api


class TestGetTokens(TestCase):
    """
    Тест получения токенов(функций контроллера Поток) из строки
    условие продления/условие вызова фазы
    """

    def test_get_tokens(self):
        string_condition = '(ddr(D21) ddr(D22) or ddr(D23) or ddr(D24) or ddr(D30)) and mr(G6)'
        tokens = user_api.Tokens(string_condition).get_tokens()
        self.generate_condition_string()
        self.assertEqual(tokens, ['ddr(D21)', 'ddr(D22)', 'ddr(D23)', 'ddr(D24)', 'ddr(D30)', 'mr(G6)'])

    def generate_condition_string(self):
        functions = ['ddr', 'ddo', 'mr', 'ddo', 'not ddr']
        condition_string = ''.join([
            f'{functions[randint(0, len(functions) - 1)]}(D{n}) and ' for n in range(1, randint(10, 20))
        ])


if __name__ == '__main__':
    main()
