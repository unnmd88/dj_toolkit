import itertools
import json
import time
from enum import Enum
from typing import Dict, Set, Tuple, List, Generator
import logging

import logging_config

logger = logging.getLogger(__name__)


class DataFields(Enum):
    sorted_stages_data = 'sorted_stages_data'
    number_of_groups = 'number_of_groups'
    number_of_stages = 'number_of_stages'
    all_num_groups = 'all_num_groups'
    sorted_all_num_groups = 'sorted_all_num_groups'
    errors = 'errors'
    allow_make_config = 'allow_make_config'
    always_red_groups = 'always_red_groups'
    always_red = 'always_red'
    always_green = 'always_green'
    conflicts = 'conflicts'
    enemy_groups = 'enemy_groups'
    stages = 'stages'
    groups_property = 'groups_property'
    type_controller = 'type_controller'
    conflict_K = '| K|'
    no_conflict_O = '| O|'
    cross_group_star_matrix = '| *|'
    base_matrix = 'base_matrix'
    conflictF997 = '03.0;'
    no_conflictF997 = '  . ;'
    cross_group997 = 'X;'
    matrix_F997 = 'matrix_F997'
    swarco = 'Swarco'
    peek = 'Peek'


class DataBuilder:

    matrix_output_content = ('*', 'K', 'O')

    def __init__(self, data: Dict):
        self.data = data
        self.output_matrix = None
        self.f997 = None
        self.numbers_conflicts_groups = None
        self.stages_bin_vals = None
        self.sum_conflicts = None

    def __repr__(self):

        return (f'output_matrix:\n{self._unpack_matrix(self.output_matrix)}'
                f'f997: \n{self._unpack_matrix(self.f997)}\n'
                f'f994: \n{self.numbers_conflicts_groups}\n'
                f'stages_bin_vals: {self.stages_bin_vals}\n'
                f'sum_conflicts: {self.sum_conflicts}')

    def _unpack_matrix(self, obj: List[List]) -> str:
        return '\n'.join((''.join(m) for m in obj)) + '\n'

    def create_data(self):

        num_groups = self.data[DataFields.number_of_groups.value]
        groups_property = self.data[DataFields.groups_property.value]
        all_numbers_groups = sorted(self.data[DataFields.all_num_groups.value])
        create_bin_vals_stages = self.data[DataFields.allow_make_config.value]

        self.output_matrix = [self.create_row_output_matrix(all_numbers_groups, first_row=True)]
        self.f997, self.numbers_conflicts_groups, self.stages_bin_vals = [], [], []
        self.sum_conflicts = 0

        for num_group, property_group in groups_property.items():
            enemy_groups = property_group[DataFields.enemy_groups.value]
            self.output_matrix.append(self.create_row_output_matrix(all_numbers_groups, num_group, enemy_groups))
            self.f997.append(self.create_row_f997(num_groups, num_group, enemy_groups))
            self.numbers_conflicts_groups.append(f"{';'.join(map(str, sorted(enemy_groups)))};")
            self.sum_conflicts += len(enemy_groups)
            if create_bin_vals_stages:
                self.stages_bin_vals.append(self.get_bin_val_stages(stages=property_group[DataFields.stages.value]))

    def create_row_output_matrix(
            self, all_numbers_groups: List, current_group: int = None, enemy_groups: Set = None, first_row=False
    ) -> List[str]:
        """
        Формирует строку для матрицы в виде списка.
        :param all_numbers_groups: Номер всех групп в запросе.
        :param current_group: Номер группы, для которой будет сформирован список.
        :param enemy_groups: Коллекция set из конфликтных групп для current_group.
        :param first_row: Является ли строка первой строкой матрицы("шапка")
        :return: Список-строка для матрицы конфликтов группы current_group, если first_row == False,
                 иначе список-шапка матрицы
        """

        if not first_row:
            row = [f'|0{current_group}|' if len(str(current_group)) == 1 else f'|{current_group}|']
            row += [
                DataFields.no_conflict_O.value if gr not in enemy_groups else DataFields.conflict_K.value
                for gr in all_numbers_groups
            ]
        else:
            row = [DataFields.cross_group_star_matrix.value]
            row += [f'|0{g}|' if len(str(g)) == 1 else f'|{g}|' for g in all_numbers_groups]
        return row

    def create_row_f997(self, num_groups, current_group: int, enemy_groups: Set[int]) -> List[str]:
        """
        Формирует строку матрицы для F997 конфигурации Swarco.
        :param num_groups: Количетсво групп в запросе.
        :param current_group: Номер группы, для которой будет сформирован список.
        :param enemy_groups: Коллекция set из конфликтных групп для current_group.
        :return: Список-строка для матрицы конфликтов группы current_group
        """

        row = [
            DataFields.cross_group997.value if i + 1 == current_group else
            DataFields.conflictF997.value if i + 1 in enemy_groups else DataFields.no_conflictF997.value
            for i in range(num_groups)
        ]
        return row

    def get_bin_val_stages(self, stages: Set[int]) -> int:
        """
        Формирует бинарное значение всех фаз из коллекции.
        :param stages: set с фазами, бинарное значение которых необходимо вычислить.
        :return: Бинарное значение, представленное в виде целого натурального числа.
        """

        return sum(map(lambda x: 2 ** x if x != 8 else 2 ** 0, (int(s) for s in stages)))
        # self.stages_bin_vals.append(f'{"0" * (3 - len(str(bin_val)))}{bin_val}')


class BaseConflicts:

    def __init__(self, raw_stages_data: Dict):

        self.instance_data = {
            'raw_stages_data': raw_stages_data,
            DataFields.sorted_stages_data.value: None,
            DataFields.type_controller.value: None,
            DataFields.number_of_groups.value: None,
            DataFields.number_of_stages.value: None,
            DataFields.all_num_groups.value: set(),
            DataFields.always_red_groups.value: None,
            DataFields.groups_property.value: {},
            DataFields.sorted_all_num_groups.value: None,
            DataFields.allow_make_config.value: True,
            DataFields.errors.value: []
        }

    def __repr__(self):
        return json.dumps(self.instance_data, indent=4)

    def save_json_to_file(self, json_data, file_name='conflicts.json', mode: str = 'w') -> None:
        """
        Формирует json и записывает в файл
        :param json_data: словарь, который будет записан как json
        :param file_name: путь к файлу
        :param mode: режим записи в файл
        :return:
        """

        self.set_to_list(json_data)

        with open(file_name, mode, encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
            f.write('\n\n')

    def set_to_list(self, target: Dict):
        """
        Рекурсивно превращает множества set в список list значения словаря target.
        :param target: словарь, в котом значения set необходмио заменить на list
        :return:
        """

        for k, v in target.items():
            if isinstance(v, dict):
                self.set_to_list(v)
            elif isinstance(v, set):
                target[k] = sorted(v)

    def create_data_for_calculate_conflicts(self, separator: str = ','):
        """
        Формирует данные для расчёта конфликтов. Определяет возможность формирования конфига .PTC2 или .DAT
        по следующему правилу: если все группы представляют собой однозначные целые числа int, то
        allow_make_config == True. Если присутствуют группы типа 5.1, 5.2(определяю как float), то
        allow_make_config ==False.
        :param separator: разделитель для формирования списка направлений
        :return:
        """

        processed_stages = {}
        stage = None
        unsorted_num_groups = self.instance_data[DataFields.all_num_groups.value]
        try:
            for stage, groups in self.instance_data['raw_stages_data'].items():
                unsorted_stages = {int(g) if g.isdigit() else float(g) for g in groups.split(separator) if g}
                processed_stages[stage] = unsorted_stages
                unsorted_num_groups |= unsorted_stages
        except ValueError as err:
            self.instance_data[DataFields.errors.value].append(
                f'Некорректный номер направления у фазы '
                f'{stage}: {str(err).split(":")[-1].replace(" ", "")}, должен быть числом'
            )

        if not self.check_data_for_calculate_is_valid(max(unsorted_num_groups), len(processed_stages.keys())):
            return

        unsorted_all_num_groups, always_red_groups = self.get_always_red_and_all_unsorted_groups(unsorted_num_groups)
        self.add_data_to_instance_data_dict_for_calc_conflicts(
            processed_stages, unsorted_all_num_groups, always_red_groups
        )

    def check_data_for_calculate_is_valid(self, num_groups: int, num_stages: int):
        """
        Проверяет валидное количество направлений и фаз. Если передано недопустимое количество фаз
        и направлений, добавляет сообщение об ошибке в self.instance_data[DataFields.number_of_stages.value] и
        возвращает Falsе, иначе возвращает True
        :param num_groups: Количество группю
        :param num_stages: Количество фаз
        :return: True, если количество направлений и фаз допустимо, иначе False.
        """

        self.instance_data[DataFields.number_of_groups.value] = num_groups
        self.instance_data[DataFields.number_of_stages.value] = num_stages
        if num_groups > 48:
            self.instance_data[DataFields.errors.value].append(
                f'Превышено максимально допустимое количество(48) групп: {num_groups}.'
            )
        if num_stages > 128:
            self.instance_data[DataFields.errors.value].append(
                f'Превышено максимально допустимое количество(128) фаз: {num_stages}.'
            )
        return not bool(self.instance_data[DataFields.errors.value])

    def get_always_red_and_all_unsorted_groups(self, unsorted_all_num_groups: Set) -> Tuple[Set, Set]:
        """
        Определяет для общее количество групп в виде set и группы, являющиеся "постоянно красными" в вид set
        :param unsorted_all_num_groups: set из групп, которые учатсвуют хотя бы в одной фазе.
        :return: Кортеж из set. unsorted_all_num_groups -> все номера групп, always_red_groups -> set
                 из групп, которые являются "Пост. красн."
        """

        always_red_groups = set()
        for group in range(1, max(unsorted_all_num_groups) + 1):
            if group not in unsorted_all_num_groups:
                always_red_groups.add(group)
                unsorted_all_num_groups.add(group)
        return unsorted_all_num_groups, always_red_groups

    def add_data_to_instance_data_dict_for_calc_conflicts(
            self, processed_stages: Dict, unsorted_all_num_groups: Set, all_red_groups: Set
    ):
        """
        Добавляет элементы словаря(ключ: значение) для self.instance_data
        :param all_red_groups: set из групп, которые не участвуют ни в одной фазе.
        :param processed_stages:
        :param unsorted_all_num_groups:
        :return:
        """
        self.instance_data[DataFields.sorted_stages_data.value] = processed_stages
        self.instance_data[DataFields.all_num_groups.value] = unsorted_all_num_groups
        self.instance_data[DataFields.always_red_groups.value] = all_red_groups
        self.instance_data[DataFields.allow_make_config.value] = self.make_config_allowed(processed_stages)
        self.instance_data[DataFields.sorted_all_num_groups.value] = sorted(unsorted_all_num_groups)

    def make_config_allowed(self, processed_stages: Dict[str, Set]):
        """
        Проверят доступность создания конфигурационного файла .PTC2/.DAT
        Если одно из направлений или одна из фаз не является целым числом, возвращает False, иначе True.
        :param processed_stages: Словарь вида {фаза: направления}, например:
                                 "1": {1, 2, 4, 5}, "2": {4, 5, 6}, "3": {6, 7, 8}
        :return: True если все направления и фазы представлены в виде целым числом, иначе False
        """

        for stage, groups_in_stage in processed_stages.items():
            if not stage.isdigit() or not all(isinstance(g, int) for g in groups_in_stage):
                return False
        return True

    def calculate_conflicts(self) -> None:
        """
        Формирует словарь для всех групп с данными о группе: конфликтами и фазами, в которых участвует направеление
        :return: None
        """

        groups_prop = self.instance_data[DataFields.groups_property.value]
        for group in self.instance_data.get(DataFields.sorted_all_num_groups.value):
            groups_prop[group] = self.get_conflicts_and_stages_properties_for_group(group)

    def get_conflicts_and_stages_properties_for_group(self, num_group: int):
        """
        Формирует конфликты для группы.
        :param num_group: Номер группы, для котороый будут сформированы конфликты в виде set
        :return: Словарь data для num_group вида:
                 {
                  'stages': {фазы(в которых участвует num_group) типа str},
                  'enemy_groups': {группы, с которыми есть конфликт у группы num_group типа str}
                 }
                Пример data: {'stages': {'1', '2'}, 'enemy_groups': {'4', '5', '6'}}
        """

        group_in_stages = set()
        conflict_groups = {g for g in self.instance_data[DataFields.all_num_groups.value] if g != num_group}
        for stage, groups_in_stage in self.instance_data[DataFields.sorted_stages_data.value].items():
            if num_group in groups_in_stage:
                group_in_stages.add(stage)
                for g in groups_in_stage:
                    conflict_groups.discard(g)
        assert conflict_groups == self.supervisor_conflicts(num_group)
        is_always_red: bool = False if group_in_stages else True
        is_always_green: bool = group_in_stages == set(self.instance_data[DataFields.sorted_stages_data.value].keys())
        assert not ((is_always_red is True) and (is_always_green is True))
        data = {
            DataFields.stages.value: group_in_stages,
            DataFields.enemy_groups.value: conflict_groups,
            DataFields.always_red.value: is_always_red,
            DataFields.always_green.value: is_always_green
        }
        return data

    def supervisor_conflicts(self, num_group: int) -> Set:
        """
        Метод формирует set из групп, с которыми есть конфликт у группы num_group. Является проверкой
        корректности формирования конфликтных групп метода self.get_conflicts_and_stages_for_group.
        Алгоритм формирования set из конфликтных групп:
        В цикле перебираем все группы из self.instance_data[DataFields.sorted_all_num_groups.value] и
        смотрим, если num_group и очередная перебираемая группа не присутсвуют вместе ни в одной фазе, то
        добавляем очередную перебираемую группу(g) в множество enemy_groups.
        :param num_group: Номер группы, для которой будет сформировано set конфликтных групп
        :return: set из конфликтных групп для группы num_group
        """

        enemy_groups = set()
        for group in (g for g in self.instance_data[DataFields.sorted_all_num_groups.value] if g != num_group):
            for groups_in_stage in self.instance_data[DataFields.sorted_stages_data.value].values():
                if {num_group, group}.issubset(groups_in_stage):
                    break
            else:
                enemy_groups.add(group)
        return enemy_groups

    def calculate(self, create_json=False):
        """
        Последовательное выполнений методов, приводящее к формированию полного результата расчёта
        конфликтов и остальных свойств.
        :return:
        """

        functions: tuple = self.create_data_for_calculate_conflicts, self.calculate_conflicts
        for func in functions:
            if self.instance_data[DataFields.errors.value]:
                break
            func()
        if create_json:
            self.save_json_to_file(self.instance_data)
        else:
            self.set_to_list(self.instance_data)

        data = DataBuilder(self.instance_data)
        data.create_data(

        )
        print(data)


class SwarcoConflicts(BaseConflicts):
    def __init__(self, raw_stages_data):
        super().__init__(raw_stages_data)
        self.instance_data[DataFields.type_controller.value] = 'Swarco'

    def calculate(self, create_json=False):
        """
        Последовательное выполнений методов, приводящее к формированию полного результата расчёта
        конфликтов и остальных свойств.
        :return:
        """

        super().calculate(create_json=True)
        logger.debug('DDD calculate')

    def stages_bin_val(self):
        pass


if __name__ == '__main__':
    logger.debug('DDD')
    logger.info('IIII')
    example = {
        '1': '1,4,2,3,5,5,5,5,3,4,2',
        '2': '1,6,7,7,3',
        '3': '9,10,8,13,3,10,',
        '4': '5,6,4'
    }
    start_time = time.time()
    obj = SwarcoConflicts(example)
    obj.calculate(create_json=True)
    print(f'ВРемя выполеения составило: {time.time() - start_time}')
    # print(obj)
    # for m in obj.instance_data[DataFields.base_matrix.value]:
    #     print(m)
