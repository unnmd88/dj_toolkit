import json
import pprint
import time
from enum import Enum
from typing import Dict, Set
import logging

example = {
    '1': '1,4,2,3,5,5,5,5,3,4,2',
    '2': '1,6,7,7,',
    '3': '9,10,8,13'
}

logger = logging.getLogger(__name__)


class DataFields(Enum):
    sorted_stages_data = 'sorted_stages_data'
    max_group = 'max_group'
    all_num_groups = 'all_num_groups'
    sorted_all_num_groups = 'sorted_all_num_groups'
    errors = 'errors'
    allow_make_config = 'allow_make_config'
    all_red_groups = 'all_red_groups'
    conflicts = 'conflicts'
    enemy_groups = 'enemy_groups'
    stages = 'stages'
    groups_property = 'groups_property'


class Conflicts:

    def __init__(self, raw_stages_data: Dict):

        self.instance_data = {
            'raw_stages_data': raw_stages_data,
            DataFields.sorted_stages_data.value: None,
            DataFields.max_group.value: None,
            DataFields.all_num_groups.value: set(),
            DataFields.all_red_groups.value: set(),
            DataFields.groups_property.value: {},
            DataFields.sorted_all_num_groups.value: None,
            DataFields.allow_make_config.value: None,
            DataFields.errors.value: []
        }

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

    def set_to_list(self, target):
        for k, v in target.items():
            if isinstance(v, dict):
                self.set_to_list(v)
            elif isinstance(v, set):
                target[k] = sorted(v)

    def create_data_for_calculate_conflicts(self, separator: str = ','):
        """
        Формирует sorted_stages_data и max_group для self.instance_data
        :param separator: разделитель для формирования списка направлений
        :return:
        """

        processed_stages = {}
        stage = None
        unsorted_all_num_groups = self.instance_data[DataFields.all_num_groups.value]
        try:
            for stage, groups in self.instance_data['raw_stages_data'].items():
                unsorted_stages = {int(g) if g.isdigit() else float(g) for g in groups.split(separator) if g}
                processed_stages[stage] = unsorted_stages
                unsorted_all_num_groups |= unsorted_stages
        except ValueError as err:
            self.instance_data['errors'].append(
                f'Некорректный номер направления у фазы '
                f'{stage}: {str(err).split(":")[-1].replace(" ", "")}, должен быть числом'
            )
        self.get_all_red_and_max_group(unsorted_all_num_groups)
        self.add_data_to_instance_data_dict_for_calc_conflicts(processed_stages, unsorted_all_num_groups)
        pprint.pprint(self.instance_data)

    def get_all_red_and_max_group(self, unsorted_all_num_groups: Set):
        for group in range(1, max(unsorted_all_num_groups) + 1):
            if group not in unsorted_all_num_groups:
                self.instance_data[DataFields.all_red_groups.value].add(group)
                unsorted_all_num_groups.add(group)

    def add_data_to_instance_data_dict_for_calc_conflicts(self, processed_stages: Dict, unsorted_all_num_groups: Set):
        self.instance_data[DataFields.sorted_stages_data.value] = processed_stages
        self.instance_data[DataFields.all_num_groups.value] = unsorted_all_num_groups
        self.instance_data[DataFields.allow_make_config.value] = all(
            isinstance(g, int) for g in unsorted_all_num_groups)
        self.instance_data[DataFields.max_group.value] = len(self.instance_data[DataFields.all_num_groups.value])
        self.instance_data[DataFields.sorted_all_num_groups.value] = sorted(unsorted_all_num_groups)

    def calculate_conflicts(self):

        groups_prop = self.instance_data[DataFields.groups_property.value]
        for group in self.instance_data.get(DataFields.sorted_all_num_groups.value):
            groups_prop[group] = self.get_conflicts_and_stages_for_group(group)
        pprint.pprint(self.instance_data)

    def get_conflicts_and_stages_for_group(self, num_group: int):
        """
        Формирует конфликты для группы.
        :param num_group: Номер группы, для котороый будут сформированы конфликты в виде set
        :return: Словарь data для num_group вида:
                 {'stages': {фазы(в которых участвует num_group) типа str},
                  'enemy_groups': {группы, с которыми есть конфликт у группы num_group типа str}
                 }
                Пример data: {'stages': {'1', '2'}, 'enemy_groups': {'4', '5', '6'}}
        """

        num_group_in_stages = set()
        conflict_groups = {g for g in self.instance_data[DataFields.all_num_groups.value] if g != num_group}
        for stage, groups_in_stage in self.instance_data[DataFields.sorted_stages_data.value].items():
            if num_group in groups_in_stage:
                num_group_in_stages.add(stage)
                for g in groups_in_stage:
                    conflict_groups.discard(g)
        assert conflict_groups == self.supervisor_conflicts(num_group)
        data = {
            DataFields.stages.value: num_group_in_stages,
            DataFields.enemy_groups.value: conflict_groups
        }
        return data

    def supervisor_conflicts(self, num_group: int) -> Set:
        """
        Метод формирует set из групп, с которыми есть конфликт у группы num_group. Является проверкой
        корректности формирования конфликтных групп метода self.calculate_conflicts.
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




    def calculate(self):
        self.create_data_for_calculate_conflicts()
        self.calculate_conflicts()
        self.save_json_to_file(self.instance_data)


if __name__ == '__main__':
    from engineering_tools.settings import LOGGING

    start_time = time.time()
    obj = Conflicts(example)
    obj.calculate()
    print(f'ВРемя выполеения составило: {time.time() - start_time}')
