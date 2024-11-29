from unittest import TestCase, main


class TestPotokP(TestCase):
    def setUp(self) -> None:
        self.base_http = 'http://127.0.0.1:8000/'

    def test_get_responce(self):
        self.assertTrue()
        self.assertEqual(self.host.convert_val_to_num_stage_get_req('0x1000'), 13)
        self.assertEqual(self.host.convert_val_to_num_stage_get_req('@'), 7)


if __name__ == '__main__':
    main()