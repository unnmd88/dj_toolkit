from enum import StrEnum

class CmdSg(StrEnum):
    GREEN = '3'
    RED = '1'
    DISABLED = '0'


class BaseStream:

    def __init__(self, source_cmd_sg, xp, max_groups, start_stage_in_xp):
        self.xp = xp
        self.start_stage_in_xp = start_stage_in_xp
        self.source_cmd_sg = source_cmd_sg
        self.max_groups = max_groups
        self.calculated_stages_and_groups = self.get_stages(source_cmd_sg, start_stage_in_xp)
        self.groups_in_xp = self.get_groups_in_xp(self.calculated_stages_and_groups)

    def get_stages(self, current_cmdSG: list[str], start_logical_stage: int):
        res = {}
        for num, groups_in_stage in enumerate(current_cmdSG, start_logical_stage):
            _groups_in_stage = groups_in_stage.split(',')
            res[str(num)] = ','.join([str(i) for i, g in enumerate(_groups_in_stage, 1) if g == CmdSg.GREEN])
        self.calculated_stages_and_groups = res
        return res

    def get_groups_in_xp(self, data: dict):

        a_set = set()
        for g in data.values():
            a_set |= set(g.split(','))
        self.groups_in_xp = a_set
        return a_set

    def get_cmdSG_line(self, groups_in_xp: set, groups_in_curr_stage: str):
        g_split = set(groups_in_curr_stage.split(','))

        print(f'groups_in_xp: {groups_in_xp}')
        values_cmd_sg = []
        for num_g in range(1, self.max_groups + 1):
            num_g_str = str(num_g)
            if not num_g_str in groups_in_xp:
                val = CmdSg.DISABLED
            elif num_g_str in g_split:
                val = CmdSg.GREEN
            else:
                val = CmdSg.RED
            values_cmd_sg.append(val)
        return values_cmd_sg

    def write(self):

        with open('413_stages_new.txt', 'w') as f:
            f.write(f'xp {self.xp}: \n'
                    f'Группы: {",".join(list(map(str, sorted(map(int, self.groups_in_xp)))))}\n')
            for num_stage, groups in self.calculated_stages_and_groups.items():
                cmdSG = self.get_cmdSG_line(self.groups_in_xp, groups)
                f.write(f'stage {num_stage}:\n'
                        f'{groups}\n'
                        f'{",".join(cmdSG)}\n{"-" * 40}\n')
            f.write(f'\n')

    def repair_cmd_sg(self):
        acc = []
        for stage_cmd_sg in self.source_xp_cmd_sg:
            acc.append(
                [val if str(num_group) in self.groups_in_xp else CmdSg.DISABLED.value for num_group, val in
                 enumerate(stage_cmd_sg.split(','), 1)]
            )
        self.repaired_xp_cmd_sg = acc
        print(*acc, sep='\n')

class Repair:

    def __init__(self, xp, groups_in_xp, source_xp_cmd_sg):
        self.xp = xp
        self.groups_in_xp = set(map(str, groups_in_xp))
        self.source_xp_cmd_sg = source_xp_cmd_sg
        self.repaired_xp_cmd_sg = None

    def repair_cmd_sg(self):
        acc = []
        for stage_cmd_sg in self.source_xp_cmd_sg:
            acc.append(
                [val if str(num_group) in self.groups_in_xp else CmdSg.DISABLED.value for num_group, val in
                 enumerate(stage_cmd_sg.split(','), 1)]
            )
        self.repaired_xp_cmd_sg = acc
        print(*acc, sep='\n')

    def write(self):
        with open('413_stages_new.txt', 'w') as f:
            f.write(f'xp {self.xp}: \n'
                    f'Группы: {",".join(list(map(str, sorted(map(int, self.groups_in_xp)))))}\n')
            for num_stage, groups in self.calculated_stages_and_groups.items():
                cmdSG = self.get_cmdSG_line(self.groups_in_xp, groups)
                f.write(f'stage {num_stage}:\n'
                        f'{groups}\n'
                        f'{",".join(cmdSG)}\n{"-" * 40}\n')
            f.write(f'\n')

XP1_STAGES = [
    ('3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,3,0,1,0,3,3,0,0,0,0,0,0,1,0,1,1,3,0,0,3,1,1,1,1,1,1,1,1,1,1,1'),
    ('3,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,3,1,0,1,0,3,3,0,0,0,0,0,0,1,0,1,3,1,0,0,1,3,1,1,1,1,1,1,1,1,1,1'),
    ('3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,3,0,1,0,3,3,0,0,0,0,0,0,1,0,1,1,3,0,0,1,1,3,1,1,1,1,1,1,1,1,1'),
    ('3,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,3,1,0,1,0,3,3,0,0,0,0,0,0,1,0,1,3,1,0,0,1,1,1,3,1,1,1,1,1,1,1,1'),
    ('3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,3,0,1,0,3,3,0,0,0,0,0,0,1,0,1,1,3,0,0,1,1,1,1,3,1,1,1,1,1,1,1'),
    ('1,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,3,1,0,0,0,0,0,1,1,0,3,0,1,1,0,0,0,0,0,0,3,0,3,3,1,0,0,1,1,1,1,1,3,1,1,1,1,1,1'),
    ('1,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,3,3,0,0,0,0,0,1,1,0,3,0,1,1,0,0,0,0,0,0,3,0,1,3,1,0,0,1,1,1,1,1,1,3,1,1,1,1,1'),
    ('3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,3,0,1,0,3,3,0,0,0,0,0,0,1,0,1,1,3,0,0,1,1,1,1,1,1,1,3,1,1,1,1'),
    ('1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,1,0,1,0,3,1,0,0,0,0,0,0,1,0,1,1,3,0,0,1,1,1,1,1,1,1,1,3,1,1,1'),
    ('3,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,3,1,0,1,0,3,3,0,0,0,0,0,0,1,0,1,3,1,0,0,1,1,1,1,1,1,1,1,1,3,1,1'),
    ('3,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,3,0,0,0,0,0,1,1,0,1,0,3,1,0,0,0,0,0,0,3,0,1,3,1,0,0,1,1,1,1,1,1,1,1,1,1,3,1'),
    ('1,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,3,3,0,0,0,0,0,1,1,0,3,0,1,1,0,0,0,0,0,0,3,0,1,3,1,0,0,1,1,1,1,1,1,1,1,1,1,1,3')
]




xp1 = BaseStream(XP1_STAGES, 1, 60, 1)
# xp1.write()