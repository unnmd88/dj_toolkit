import typing

from django.db import models, IntegrityError
from django.utils import timezone

from toolkit.sdp_lib.management_controllers.controller_management import AvailableControllers


# Create your models here.


class SaveConfigFiles(models.Model):
    source = models.CharField(max_length=20)
    file = models.FileField(upload_to='conflicts/configs/', null=True, verbose_name='config_file')
    time_create = models.DateTimeField(default=timezone.now)
    controller_type = models.CharField(max_length=20, db_index=True, default='undefined')
    description = models.TextField(null=True)
    number = models.CharField(max_length=100, null=True)
    ip_adress = models.CharField(max_length=20, null=True)
    address = models.TextField(blank=True, null=True)

    def __repr__(self):
        return self.file.name


class SaveConflictsTXT(models.Model):
    source = models.CharField(max_length=20)
    file = models.FileField(upload_to='conflicts/txt/', null=True, verbose_name='txt_files')
    time_create = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return self.file.name


class ControllerManagement(models.Model):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    # num_visible_hosts = models.CharField(max_length=2, blank=False, null=False, default='1')
    num_visible_hosts = models.IntegerField(default=1, blank=True)
    data = models.TextField(unique=True)
    # data = models.JSONField(unique=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    category = models.IntegerField()
    user_name = models.CharField(max_length=20, default='0')

    def __str__(self):
        return self.name


class TrafficLightsObjects(models.Model):
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True)
    type_controller = models.CharField(max_length=20)
    group = models.IntegerField(default=0)
    ip_adress = models.CharField(max_length=20, null=True)
    address = models.TextField(blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.number} {self.address} {self.type_controller}'


class TelegrammUsers(models.Model):
    chat_id = models.CharField(max_length=10, unique=True)
    username = models.CharField(max_length=40, null=True)
    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=40, null=True)
    access_level = models.IntegerField(default=0)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.chat_id} {self.username} {self.first_name} {self.username} {self.access_level}'


class TrafficLightConfigurator(models.Model):
    function = models.CharField(max_length=255, verbose_name='Тип запроса')
    condition_string = models.TextField(verbose_name='Условие из tlc')
    function_values = models.TextField(max_length=255, verbose_name='Значения функций', default='')
    condition_string_for_parse = models.TextField(verbose_name='Условие с заданными значениями функций', default='')
    tokens = models.TextField(max_length=255, verbose_name='Функции(токены) из условия tlc', default='')
    result_condition_value = models.BooleanField(
        verbose_name='Результат выражения условия из tlc для заданных функций', default='', null=True
    )
    errors = models.CharField(max_length=255, verbose_name='Ошибки')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')


class DefaultControllerManagementOptions(typing.NamedTuple):
    type_controller: str
    group: int
    commands: str
    max_stage: int
    options: str | None = None
    sources: str | None = None


# swarco_default_controller_management_options = DefaultControllerManagementOptions(
#     type_controller = AvailableControllers.SWARCO.value,
#     group = 1,
#     commands = 'set_stage',
#     max_stage = 8,
#     options = None,
#     sources = 'man'
# )
#
# potokS_default_controller_management_options = DefaultControllerManagementOptions(
#     type_controller = AvailableControllers.POTOK_S.value,
#     group = 2,
#     commands = 'set_stage',
#     max_stage = 128,
#     options = None,
#     sources = None
# )
#
# potokP_default_controller_management_options = DefaultControllerManagementOptions(
#     type_controller = AvailableControllers.POTOK_P.value,
#     group = 3,
#     commands = 'set_stage',
#     max_stage = 128,
#     options = None,
#     sources = None
# )
#
# peek_default_controller_management_options = DefaultControllerManagementOptions(
#     type_controller = AvailableControllers.POTOK_P.value,
#     group = 2,
#     commands = 'set_stage',
#     max_stage = 128,
#     options = None,
#     sources = None
# )

class ControllerManagementOptions(models.Model):

    type_controller = models.CharField(max_length=20, unique=True)
    group = models.IntegerField(default=0, unique=True)
    commands = models.CharField(max_length=40)
    min_val = models.IntegerField(default=0)
    max_val = models.IntegerField()
    options = models.CharField(max_length=255, null=True)
    sources = models.CharField(max_length=255, null=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f'type_controller: {self.type_controller}\n'
            f'group: {self.group}\n'
            f'commands: {self.commands}\n'
            f'max_stage: {self.max_stage}\n'
            f'options: {self.options}\n'
            f'sources: {self.sources}'
        )

    @property
    def swarco_default(self) -> DefaultControllerManagementOptions:
        return DefaultControllerManagementOptions(
            type_controller = AvailableControllers.SWARCO.value,
            group = 1,
            commands = 'set_stage',
            max_stage = 8,
            options = None,
            sources = 'man'
        )

    @property
    def peek_default(self) -> DefaultControllerManagementOptions:
        return DefaultControllerManagementOptions(
            type_controller = AvailableControllers.PEEK.value,
            group = 2,
            commands = 'set_stage',
            max_stage = 32,
            options = None,
            sources = 'central'
        )

    @property
    def potok_p_default(self) -> DefaultControllerManagementOptions:
        return DefaultControllerManagementOptions(
            type_controller = AvailableControllers.POTOK_S.value,
            group = 3,
            commands = 'set_stage',
            max_stage = 128,
            options = None,
            sources = None
        )

    @property
    def potok_s_default(self) -> DefaultControllerManagementOptions:
        return DefaultControllerManagementOptions(
            type_controller = AvailableControllers.POTOK_S.value,
            group = 2,
            commands = 'set_stage',
            max_stage = 128,
            options = None,
            sources = None
        )

    @property
    def matches_default(self) -> dict[str, DefaultControllerManagementOptions]:
        return {
            AvailableControllers.SWARCO.value: self.swarco_default,
            AvailableControllers.POTOK_P.value: self.potok_p_default,
            AvailableControllers.POTOK_S.value: self.potok_s_default,
            AvailableControllers.PEEK.value: self.peek_default
        }

    def get_default_props(self, type_controller) -> DefaultControllerManagementOptions:
        return self.matches_default.get(type_controller)


def create_defaults_controller_management_options(create_objects=False):

    swarco_default_controller_management_options = DefaultControllerManagementOptions(
        type_controller = AvailableControllers.SWARCO.value,
        group = 1,
        commands = 'set_stage',
        max_stage = 8,
        options = None,
        sources = 'man'
    )

    peek_default_controller_management_options = DefaultControllerManagementOptions(
        type_controller = AvailableControllers.PEEK.value,
        group = 2,
        commands = 'set_stage',
        max_stage = 32,
        options = None,
        sources = None
    )

    potokP_default_controller_management_options = DefaultControllerManagementOptions(
        type_controller = AvailableControllers.POTOK_P.value,
        group = 3,
        commands = 'set_stage',
        max_stage = 128,
        options = None,
        sources = None
    )

    potokS_default_controller_management_options = DefaultControllerManagementOptions(
        type_controller = AvailableControllers.POTOK_S.value,
        group = 4,
        commands = 'set_stage',
        max_stage = 128,
        options = None,
        sources = None
    )
    objs = (
        swarco_default_controller_management_options,
        potokP_default_controller_management_options,
        potokS_default_controller_management_options,
        peek_default_controller_management_options
    )

    if create_objects:
        saved = []
        for opt in objs:
            try:
                saved.append(ControllerManagementOptions.objects.create(**opt._asdict()))
            except IntegrityError:
                pass
        return saved

    return (
        swarco_default_controller_management_options,
        potokP_default_controller_management_options,
        potokS_default_controller_management_options,
        peek_default_controller_management_options
    )


if __name__ == '__main__':
    o = create_defaults_controller_management_options()
    print(o)
    for f in o:
        print(f._asdict())


