from enum import Enum
from typing import Dict
import logging

example = {
    '1': '1,4,2,3,5,5,5,5,3,4,2',
    '2': '1,6,7.1,7.2',
    '3': '9,10'
}

logger = logging.getLogger(__name__)


class DataFields(Enum):
    sorted_stages_data = 'sorted_stages_data'
    max_group = 'max_group'
    all_num_groups = 'all_num_groups'
    errors = 'errors'


class Conflicts:
    def __init__(self, raw_stages_data: Dict):

        self.instance_data = {
            'raw_stages_data': raw_stages_data,
            DataFields.sorted_stages_data.value: None,
            DataFields.max_group.value: None,
            DataFields.all_num_groups.value: None,
            DataFields.errors.value: []
        }

    def sorting_stages_and_groups(self, separator: str = ','):
        """
        Формирует sorted_stages_data и max_group для self.instance_data
        :param separator: разделитель для формирования списка направлений
        :return:
        """

        processed_stages = {}
        all_groups = set()
        stage = None
        try:
            for stage, groups in self.instance_data['raw_stages_data'].items():
                unsorted_stages = {int(g) if g.isdigit() else float(g) for g in groups.split(separator)}
                processed_stages[stage] = unsorted_stages
                all_groups |= unsorted_stages
        except ValueError as err:
            self.instance_data['errors'].append(
                f'Некорректный номер направления у фазы '
                f'{stage}: {str(err).split(":")[-1].replace(" ", "")}, должен быть числом'
            )

        self.instance_data[DataFields.sorted_stages_data.value] = processed_stages
        self.instance_data[DataFields.max_group.value] = len(all_groups)
        self.instance_data[DataFields.all_num_groups.value] = all_groups

        logger.debug(f'max_group: {len(all_groups)}')
        logger.debug(f'all_num_groups : {all_groups}')
        logger.debug(f'self.sorted_stages_data : {processed_stages}')
        logger.debug(f'self.instance_data: {self.instance_data}')
        logger.debug(f'self.instance_data: {self.instance_data}')


if __name__ == '__main__':
    from engineering_tools.settings import LOGGING

    obj = Conflicts(example)
    obj.sorting_stages_and_groups()
