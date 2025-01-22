
from toolkit.tmp_py_files.cmd_sg.calculate import CmdSg

class Calculate:

    def __init__(self, xp, groups_in_xp, source_xp_cmd_sg):
        self.xp = xp
        self.groups_in_xp = set(map(str, groups_in_xp))
        self.source_xp_cmd_sg = source_xp_cmd_sg
        self.repaired_xp_cmd_sg = None
        print(f'self.groups_in_xp: {self.groups_in_xp}')

    def repair_cmd_sg(self):
        acc = []
        for stage_cmd_sg in self.source_xp_cmd_sg:
            acc.append(
                ",".join([
                    val if str(num_group) in self.groups_in_xp else CmdSg.DISABLED.value
                    for num_group, val in enumerate(stage_cmd_sg.split(','), 1)
                ])
            )
        self.repaired_xp_cmd_sg = acc
        print(f'Process {self.xp}')
        print(*acc, sep='\n')

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
groups_in_xp2 = {2,12,13,14,15,31,33,41}
groups_in_xp3 = {9,27,37}
groups_in_xp4 = {3,5,6,7,8,10,11,16,17,18,19,21,24,25,26,28,36,38,39,40,43,47,48}
xp1_cmd_sg = [
    ('3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1'),
    ('3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1'),
    ('3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1'),
    ('3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1'),
    ('3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1'),
    ('1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,1,1,3,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1'),
    ('1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1'),
    ('3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1'),
    ('3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1'),
    ('3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1'),
    ('1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3'),
]
xp2_cmd_sg = [
    ('1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,3,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,3,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
]
xp3_cmd_sg = [
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
]
xp4_cmd_sg =  [
    ('1,1,3,1,1,1,3,3,1,3,3,1,1,1,1,3,1,1,1,1,3,1,1,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,3,1,1,1,3,3,1,1,3,1,1,1,1,3,3,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,3,1,3,1,1,1,1,1,3,1,1,1,1,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,3,3,3,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,3,3,1,1,1,3,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,3,3,3,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,3,1,1,1,1,1,1,3,3,1,1,1,1,3,1,1,1,1,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,3,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,3,1,1,3,3,1,1,1,1,1,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,3,3,1,1,1,3,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,3,3,3,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,3,1,1,1,3,3,1,3,1,1,1,1,1,3,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,3,3,3,1,3,1,1,1,1,1,1,1,1,1,1,3,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
    ('1,1,1,1,1,3,3,3,1,1,3,1,1,1,1,1,3,3,1,1,3,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'),
]


xp1 = Calculate(1, groups_in_xp1, xp1_cmd_sg)
xp1.repair_cmd_sg()
print(f'{"*" * 120}')
xp2 = Calculate(2, groups_in_xp2, xp2_cmd_sg)
xp2.repair_cmd_sg()
print(f'{"*" * 120}')
xp3 = Calculate(3, groups_in_xp3, xp3_cmd_sg)
xp3.repair_cmd_sg()
print(f'{"*" * 120}')
xp4 = Calculate(4, groups_in_xp4, xp4_cmd_sg)
xp4.repair_cmd_sg()