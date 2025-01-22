import functools
import operator
from typing import List, Tuple

from toolkit.tmp_py_files.cmd_sg.calculate import CmdSg


class Intersection:

    def __init__(self, xp, groups_in_xp, source_xp_cmd_sg):
        self.xp = xp
        self.groups_in_xp = set(map(str, groups_in_xp))
        self.source_cmd_sg = source_xp_cmd_sg
        self.repaired_cmd_sg = None

    def __repr__(self):
        return (f'Process: {self.xp}\n'
                f'Groups in process: {", ".join(list(map(str, sorted(map(int, self.groups_in_xp)))))}\n'
                f'Groups in CmdSG source:\n{self.make_pretty_cmd_sg(self.source_cmd_sg)}'
                f'Groups in CmdSG repaired:\n{self.make_pretty_cmd_sg(self.repaired_cmd_sg)}')

    def __add__(self, other):
        if isinstance(other, Intersection):
            return f'{repr(self)}\n{repr(other)}'
        return NotImplemented

    def make_pretty_cmd_sg(self, cmd_sg: List[str]) -> str:
        """
        Формирует строки CmdSG из "Process" EC-X Configurator для удобного вывода/записи в файл.
        :param cmd_sg: Список строк CmdSG.
        :return: Удобочитаемая строка для вывода/записи в файл.
        """
        if cmd_sg is not None:
            data = ''
            for num_stage, cmd_sg_stage in enumerate(cmd_sg, 1):
                data += f'Stage{" " * (2 if num_stage < 10 else 1)}{num_stage}: {cmd_sg_stage}' + '\n'
            return data

    def repair_cmd_sg_all_stages(self):
        """
        Заменяет значение группы в строке процесса CmdSG на 0, если группа не участвует в процессе
        для всех фаз процесса.
        :return: Список строк CmdSG, где индекс + 1 -> номер фазы
        """
        self.repaired_cmd_sg = [self._repair_line_stage(line_stage) for line_stage in self.source_cmd_sg]
        return self.repaired_cmd_sg

    def _repair_line_stage(self, line_stage: str):
        """
        Заменяет значение группы в строке line_stage на 0, если группа не участвует в процессе.
        :param line_stage: строка CmdSG из "Process" EC-X Configurator
        :return: скорректированная строка CmdSG, которую можно скопировать в "Process" EC-X Configurator
        """
        return ",".join([
            val if str(num_group) in self.groups_in_xp else CmdSg.DISABLED.value
            for num_group, val in enumerate(line_stage.split(','), 1)
        ])


    def read_cmd_sg(self):
        with open('CO413.DAT') as f:
            acc = []
            for line in f:

                if 'CmdSG' in line and len(line) > 20:
                    acc.append(line)
        print(*acc)
        print(len(acc))

    # def write(self):
    #     with open('413_stages_new.txt', 'w') as f:
    #         f.write(f'xp {self.xp}: \n'
    #                 f'Группы: {",".join(list(map(str, sorted(map(int, self.groups_in_xp)))))}\n')
    #         for num_stage, groups in self.calculated_stages_and_groups.items():
    #             cmdSG = self.get_cmdSG_line(self.groups_in_xp, groups)
    #             f.write(f'stage {num_stage}:\n'
    #                     f'{groups}\n'
    #                     f'{",".join(cmdSG)}\n{"-" * 40}\n')
    #         f.write(f'\n')


groups_in_xp1 = {1,4,20,22,23,29,30,32,34,35,42,44,45,46,49,50,51,52,53,54,55,56,57,58,59,60}
xp1_cmd_sg = [
    '3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1',
    '3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1',
    '3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1',
    '3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1',
    '3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1',
    '1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,1,1,3,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1',
    '1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1',
    '3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1',
    '1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1',
    '3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1',
    '3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1',
    '1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3',
]

groups_in_xp2 = {2,12,13,14,15,31,33,41}
xp2_cmd_sg = [
    ('1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,3,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
]

xp1 = Intersection(xp=1, groups_in_xp=groups_in_xp1, source_xp_cmd_sg=xp1_cmd_sg)
xp1.repair_cmd_sg_all_stages()

xp2 = Intersection(xp=2, groups_in_xp=groups_in_xp2, source_xp_cmd_sg=xp2_cmd_sg)
xp2.repair_cmd_sg_all_stages()

print(xp2 + xp1)