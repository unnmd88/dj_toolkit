import json
import random
import string
import time
from enum import Enum
from typing import Dict, Set, Tuple, List, Iterator, TextIO
import logging

from toolkit.sdp_lib.utils import set_curr_datetime
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
    output_matrix = 'base_matrix'
    conflictF997 = '03.0;'
    no_conflictF997 = '  . ;'
    cross_group997 = 'X;'
    matrix_F997 = 'matrix_F997'
    numbers_conflicts_groups = 'numbers_conflicts_groups'
    stages_bin_vals = 'stages_bin_vals'
    sum_conflicts = 'sum_conflicts'
    swarco = 'Swarco'
    peek = 'Peek'


class BaseConflictsAndStages:

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
            DataFields.errors.value: [],
            DataFields.output_matrix.value: None,
            DataFields.matrix_F997.value: None,
            DataFields.numbers_conflicts_groups.value: None,
            DataFields.stages_bin_vals.value: None,
            DataFields.sum_conflicts.value: None
        }

    def get_all_data_curr_calculate(self):
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

    def _processing_data_for_calculation(self, separator: str = ','):
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

        if not self._check_data_for_calculate_is_valid(max(unsorted_num_groups), len(processed_stages.keys())):
            return

        unsorted_all_num_groups, always_red_groups = self._get_always_red_and_all_unsorted_groups(unsorted_num_groups)
        self._add_data_to_instance_data_dict_for_calc_conflicts(
            processed_stages, unsorted_all_num_groups, always_red_groups
        )

    def _check_data_for_calculate_is_valid(self, num_groups: int, num_stages: int):
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

    def _get_always_red_and_all_unsorted_groups(self, unsorted_all_num_groups: Set) -> Tuple[Set, Set]:
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

    def _add_data_to_instance_data_dict_for_calc_conflicts(
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
        self.instance_data[DataFields.allow_make_config.value] = self._make_config_allowed(processed_stages)
        self.instance_data[DataFields.sorted_all_num_groups.value] = sorted(unsorted_all_num_groups)

    def _make_config_allowed(self, processed_stages: Dict[str, Set]):
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

    def _calculate_conflicts_and_stages(self) -> None:
        """
        Формирует словарь для всех групп с данными о группе: конфликтами и фазами, в которых участвует направеление
        :return: None
        """

        groups_prop = self.instance_data[DataFields.groups_property.value]
        for group in self.instance_data.get(DataFields.sorted_all_num_groups.value):
            groups_prop[group] = self._get_conflicts_and_stages_properties_for_group(group)

    def _get_conflicts_and_stages_properties_for_group(self, num_group: int):
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
        assert conflict_groups == self._supervisor_conflicts(num_group)
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

    def _supervisor_conflicts(self, num_group: int) -> Set:
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


class OutputData(BaseConflictsAndStages):

    def __repr__(self):
        return (f'output_matrix:\n{self._unpack_matrix(self.instance_data[DataFields.output_matrix.value])}'
                f'f997: \n{self._unpack_matrix(self.instance_data[DataFields.matrix_F997.value])}\n'
                f'f994: \n{self.instance_data[DataFields.numbers_conflicts_groups.value]}\n'
                f'stages_bin_vals: {self.instance_data[DataFields.stages_bin_vals.value]}\n'
                f'sum_conflicts: {self.instance_data[DataFields.sum_conflicts.value]}')

    def _unpack_matrix(self, matrix: List[List]) -> str:
        return '\n'.join((''.join(m) for m in matrix)) + '\n'

    def _create_row_output_matrix(
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

    def _create_row_f997(self, num_groups, current_group: int, enemy_groups: Set[int]) -> List[str]:
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

    def _get_bin_val_stages(self, stages: Set[int]) -> int:
        """
        Формирует бинарное значение всех фаз из коллекции.
        :param stages: set с фазами, бинарное значение которых необходимо вычислить.
        :return: Бинарное значение, представленное в виде целого натурального числа.
        """

        return sum(map(lambda x: 2 ** x if x != 8 else 2 ** 0, (int(s) for s in stages)))

    def create_data_for_output(self):

        num_groups = self.instance_data[DataFields.number_of_groups.value]
        groups_property = self.instance_data[DataFields.groups_property.value]
        all_numbers_groups = sorted(self.instance_data[DataFields.all_num_groups.value])
        create_bin_vals_stages = self.instance_data[DataFields.allow_make_config.value]

        output_matrix = [self._create_row_output_matrix(all_numbers_groups, first_row=True)]
        f997, numbers_conflicts_groups, stages_bin_vals = [], [], []
        sum_conflicts = 0

        for num_group, property_group in groups_property.items():
            enemy_groups = property_group[DataFields.enemy_groups.value]
            output_matrix.append(self._create_row_output_matrix(all_numbers_groups, num_group, enemy_groups))
            f997.append(self._create_row_f997(num_groups, num_group, enemy_groups))
            numbers_conflicts_groups.append(f"{';'.join(map(str, sorted(enemy_groups)))};")
            sum_conflicts += len(enemy_groups)
            if create_bin_vals_stages:
                stages_bin_vals.append(self._get_bin_val_stages(stages=property_group[DataFields.stages.value]))

        self.instance_data[DataFields.output_matrix.value] = output_matrix
        self.instance_data[DataFields.matrix_F997.value] = f997
        self.instance_data[DataFields.numbers_conflicts_groups.value] = numbers_conflicts_groups
        self.instance_data[DataFields.stages_bin_vals.value] = stages_bin_vals
        self.instance_data[DataFields.sum_conflicts.value] = sum_conflicts


class CommonConflictsAndStagesAPI(OutputData):

    def __init__(self, raw_stages_data: Dict, create_txt: bool = False):
        super().__init__(raw_stages_data)
        self.instance_data[DataFields.type_controller.value] = 'Общий'
        self.create_txt = create_txt

    def create_txt_file(self):
        path_to_txt = f"calculated_data_{''.join(random.choices(string.ascii_letters, k=6))}"

        with open(path_to_txt, 'w') as f:
            logger.debug(self.instance_data[DataFields.sorted_stages_data.value])
            for stage, groups_in_stage in self.instance_data[DataFields.sorted_stages_data.value].items():
                f.write(
                    f'Фаза {stage}: {",".join(map(str, groups_in_stage))}\n'
                )
            f.write(f'Количество направлений: {self.instance_data[DataFields.number_of_groups.value]}\n\n')
            f.write('Матрица конфликтов общая:\n')
            f.write(f'{self._unpack_matrix(self.instance_data[DataFields.output_matrix.value])}\n')
            f.write('Матрица конфликтов F997 Swarco:\n')
            f.write(f'{self._unpack_matrix(self.instance_data[DataFields.matrix_F997.value])}\n')
            f.write('Конфликтные направления F994 Swarco:\n')
            f.write(f'{self._unpack_matrix(self.instance_data[DataFields.numbers_conflicts_groups.value])}\n')
            f.write('Бинарные значения фаз F009 Swarco:\n')
            for val in self.instance_data[DataFields.stages_bin_vals.value]:
                zeros = f'{"0" * 1 * (3 - len(str(val)))}'
                f.write(f'{zeros}{val};')


    def build_data(self, create_json=False):
        """
        Последовательное выполнений методов, приводящее к формированию полного результата расчёта
        конфликтов и остальных свойств.
        :return:
        """

        functions: tuple = (
            self._processing_data_for_calculation, self._calculate_conflicts_and_stages, self.create_data_for_output
        )
        for func in functions:
            if self.instance_data[DataFields.errors.value]:
                break
            func()
        if create_json:
            self.save_json_to_file(self.instance_data)
        else:
            self.set_to_list(self.instance_data)
        if self.create_txt:
            self.create_txt_file()


class SwarcoConflictsAndStagesAPI(CommonConflictsAndStagesAPI):

    def __init__(self, raw_stages_data: Dict, create_txt=False, path_to_src_config: str = None, prefix_new_config: str = 'new_'):
        super().__init__(raw_stages_data, create_txt)
        self.instance_data[DataFields.type_controller.value] = 'Swarco'
        self.path_to_src_config = path_to_src_config
        self.prefix_new_config = prefix_new_config

    def create_ptc2_config(self):
        path_to_new_PTC2 = f'{self.prefix_new_config}{self.path_to_src_config}'
        conflicts_f997 = 'NewSheet693  : Work.997'
        conflicts_f992 = 'NewSheet693  : Work.992'
        conflicts_f006 = 'NewSheet693  : Work.006'
        stage_bin_vals_f009 = 'NewSheet693  : Work.009'

        with open(self.path_to_src_config) as src, open(path_to_new_PTC2, 'w') as new_file:
            for line in src:
                if conflicts_f997 in line or conflicts_f992 in line:
                    self.write_data_to_file(
                        file_for_write=new_file,
                        file_for_read=src,
                        curr_line_from_file_for_write=line,
                        matrix=self.instance_data[DataFields.matrix_F997.value]
                    )
                elif conflicts_f006 in line:
                    self.write_data_to_file(
                        file_for_write=new_file,
                        file_for_read=src,
                        curr_line_from_file_for_write=line
                    )
                elif stage_bin_vals_f009 in line:
                    self.write_data_to_file(
                        file_for_write=new_file,
                        file_for_read=src,
                        curr_line_from_file_for_write=line,
                        stages_bin_vals=self.instance_data[DataFields.stages_bin_vals.value]
                    )
                else:
                    new_file.write(line)

    def write_data_to_file(
            self,
            file_for_write: TextIO,
            file_for_read: Iterator,
            curr_line_from_file_for_write: str,
            matrix=None,
            stages_bin_vals=None
    ):
        file_for_write.write(f'{curr_line_from_file_for_write}')
        if matrix is not None:
            for matrix_line in matrix:
                file_for_write.write(f'{"".join(matrix_line)}\n')
        elif stages_bin_vals is not None:
            for val in stages_bin_vals:
                zeros = f'{"0" * 1 * (3 - len(str(val)))}'
                file_for_write.write(f';{zeros}{val};;1;\n')
        while 'NeXt' not in curr_line_from_file_for_write:
            curr_line_from_file_for_write = next(file_for_read)
        file_for_write.write(curr_line_from_file_for_write)

    def build_data(self, create_json=False):
        super().build_data(create_json)
        if self.path_to_src_config is not None:
            self.create_ptc2_config()
        self.save_json_to_file(self.instance_data)


class PeekConflictsAndStagesAPI(CommonConflictsAndStagesAPI):
    def __init__(self, raw_stages_data):
        super().__init__(raw_stages_data)
        self.instance_data[DataFields.type_controller.value] = 'Peek'


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
    obj = SwarcoConflictsAndStagesAPI(example, create_txt=True,
                                      path_to_src_config='stripes_67_pokrovskie_vorotl_pokrovka_17_va_ot_2022_12_31_xx_JNx7t0U.PTC2')
    obj.build_data()
    print(obj)

    # obj2 = CommonConflictsAndStagesAPI(example, create_txt=True)
    # obj2.build_data()

    print(f'ВРемя выполеения составило: {time.time() - start_time}')
    # print(obj)
    # for m in obj.instance_data[DataFields.base_matrix.value]:
    #     print(m)
