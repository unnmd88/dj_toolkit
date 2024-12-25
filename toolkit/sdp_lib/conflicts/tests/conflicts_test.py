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


if __name__ == '__main__':
    main()
