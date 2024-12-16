from unittest import TestCase, main
from toolkit.sdp_lib.potok_controller import condition_parser


class TestConditionParse(TestCase):

    def test_create_valid_tokens_get_token(self):
        """
        Тест метода get_token(self). Из строки условия перехода/продления tcl контроллера Поток
        должен быть сгенерирован список с токенами(функциями) доступными для данного типа ДК
        :return:
        """

        expected_tokens = [
            'ddr(D41)', 'ddr(D41)', 'ddr(D41)', 'ddr(D45)', 'not ddr(D43)', 'ddr(D44)', 'mr(G1)', 'ddr(D41)',
            'ddr(D42)', 'ddr(D43)', 'ddr(D44)', 'ddr(D45)', 'ddr(D46)', 'ddr(D47)', 'mr(G1)', 'fctg(G1) >= 40'
        ]

        string = (
            '(ddr(D41) and (ddr(D41) or ddr(D41) or ddr(D45)) or (not ddr(D43) and ddr(D44)) and mr(G1) and '
            'ddr(D41) or ddr(D42) or ddr(D43) or ddr(D44) or ddr(D45) or ddr(D46) or ddr(D47)) and mr(G1) '
            'and fctg(G1) >= 40'
        )
        tokens = condition_parser.ConditionParser(string).create_tokens()

        self.assertEqual(tokens, expected_tokens)

        string2 = (
            '(ddr(D41))) and (ddr(D41) or ddr(D41) or ddr(D45)) or (not ddr(D43) and ddr(D44)) and mr(G1) and '
            'ddr(D41))))))))))))) or (((ddr(D42) or ddr(D43) or ddr(D44) or '
            '((((ddr(D45) or ddr(D46) or ddr(D47)) and mr(G1))))) and fctg(G1) >= 40'
        )
        tokens2 = condition_parser.ConditionParser(string2).create_tokens()
        self.assertEqual(tokens2, expected_tokens)

    def test_invalid_num_group_or_num_det_get_token(self):
        # Если номер дет > 128
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('ddr(D41) and ddr(D129)').create_tokens()
        # Если номер группы > 128
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('mr(G2) and mr(G140)').create_tokens()
        # Если номер дет начинается с 0:
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('mr(G02) and mr(G14)').create_tokens()
        # Если номер группы начинается с 0:
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('ddr(01) and ddr(D129)').create_tokens()

    def test_valid_arg_in_token(self):
        # Тест наличия аргумена D для функции детекторов
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('any_string')._get_arg('ddr', '(ddr(V15))')
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('any_string')._get_arg('ddo', '(ddo(R15))')
        # Тест наличия аргумена G или A для функции сигнальных групп
        with self.assertRaises(ValueError) as e:
            condition_parser.ConditionParser('any_string')._get_arg('fctg', '(fctg(Q2)))')
        # Тест что передана валидная функция
        with self.assertRaises(TypeError) as e:
            condition_parser.ConditionParser('any_string')._get_arg('fctgg', '(fctgg(G2)))')
        with self.assertRaises(TypeError) as e:
            condition_parser.ConditionParser('any_string')._get_arg('drr', '(drr(D2)))')


if __name__ == '__main__':
    main()
