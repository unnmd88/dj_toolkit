from unittest import TestCase, main
from toolkit.sdp_lib.conflicts.calculate_conflicts import Conflicts, DataFields


class TestConflicts(TestCase):
    def setUp(self) -> None:
        raw_data_stages = {
            '1': '1,4,2,3,5,5,5,5,3,4,2',
            '2': '1,6,7,7,3',
            '3': '9,10,8,13,3,10,',
            '4': '5,6,4'
        }
        self.current_calculation = Conflicts(raw_data_stages)
        self.current_calculation.calculate()

    def test_no_duplicates_and_sorted(self):
        """
        Проверят отсутсвие дубликатов направлений после расчёта конфликтов и отсортированность списка
        направлений в порядке возрастания
        :return:
        """

        self.assertEqual(
            self.current_calculation.instance_data[DataFields.sorted_stages_data.value]['1'],
            [1, 2, 3, 4, 5]
        )
        self.assertEqual(
            self.current_calculation.instance_data[DataFields.sorted_stages_data.value]['2'],
            [1, 3, 6, 7]
        )

    def test_num_group_and_num_stages(self):
        """
        Проверяет корректность определения количества направлений и количества фаз
        :return:
        """
        self.assertEqual(self.current_calculation.instance_data[DataFields.number_of_groups.value], 13)
        self.assertEqual(self.current_calculation.instance_data[DataFields.number_of_stages.value], 4)
        self.assertEqual(
            self.current_calculation.instance_data[DataFields.all_num_groups.value], [i for i in range(1, 14)]
        )

    def test_define_allow_make_config(self):
        """
        Проверят корректность определения ключа "allow_make_config" из словаря self.instance_data.
        :return:
        """
        self.assertTrue(
            self.current_calculation.instance_data[DataFields.allow_make_config.value], True
        )


if __name__ == '__main__':
    main()
