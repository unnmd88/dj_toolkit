"""
Модуль с т.н. "бизнес-логикой"
Если брать модель Model-View-Controller , то данный модуль относится к Controller
"""
import abc
import functools
import itertools
import json
import os
import pathlib
import shutil
import zipfile
import time
from typing import Coroutine, Dict, Tuple

from dotenv import load_dotenv
import logging

import _asyncio
import aiohttp
import asyncio
import ipaddress

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from toolkit.models import TrafficLightsObjects, SaveConfigFiles, TelegrammUsers
from toolkit.sdp_lib import controller_management, controllers
from engineering_tools.settings import MEDIA_ROOT
from .constants import (
    AvailableControllers,
    AvailableSetCommandsController,
    AvailableGetCommandsController,
    ErrorMessages,
    JsonResponceBody,
    Database,
    RequestOptions,
    AvailableTypesRequest
)

load_dotenv()
logger = logging.getLogger(__name__)


def set_curr_datetime() -> str:
    """
    Получает текущее время и дату
    :return: текущее время и дату
    """

    return controller_management.BaseCommon.set_curr_datetime()


def reverse_slashes(path: str) -> str:
    """
    Заменяет обратные слеши на прямые
    :param path: строковое представление пути до файла/катлога
    :return: строковое представление пути до файла/катлога со слешами вида "/"
    """

    return path.replace('\\', '/')


def correct_path_for_db(path: str) -> str:
    """
    Заменяет обратные слеши на прямые для пути к файлу в моделе SaveConfigFiles
    :param path: строковое представление пути до файла/катлога
    :return: строковое представление пути до файла/катлога со слешами вида "/"
    """

    return reverse_slashes(path).split('media/')[-1]


def get_controller_manager(type_request: str):
    """
    Создает объект менеждера для дальнейшего управления и взаимодействия во view функции/методе
    :param type_request: тип из api запроса
    :return: экземпляр класса, соответсвующий запросу
    """

    if type_request == RequestOptions.type_get_state.value or type_request == RequestOptions.type_get_states.value:
        manager = GetDataFromController()
    elif type_request == RequestOptions.type_set_command.value:
        manager = SetRequestToController()
    elif type_request == RequestOptions.type_get_config.value:
        manager = FileDownLoad()
    else:
        manager = None
    return manager


class QuerysetToDB:
    """
    Класс отправляет и обрабатывает запросы в БД
    """

    @staticmethod
    @sync_to_async()
    def async_db_query(param_for_search):
        queryset = TrafficLightsObjects.objects.filter(number=int(param_for_search))
        res = queryset.values()
        if res:
            res = queryset.values()[0]
        logger.debug(res)
        return res

    async def get_queryset(self, data_for_search: tuple) -> tuple:
        """
        Поиск объекта в бд по номеру/ip-address
        :param data_for_search: кортеж вида (Номер СО/IP-address из http запроса, поле поска в бд)
        :return: кортеж вида (Номер СО/IP-address из http запроса, model_to_dict(queryset)) если объект найден,
                 иначе  (Номер СО/IP-address из http запроса, None)
        """

        param, field = data_for_search
        logger.debug(data_for_search)
        if field == 'name':
            queryset = await TrafficLightsObjects.objects.filter(number=param).afirst()
        elif field == 'ipAddress':
            queryset = await TrafficLightsObjects.objects.filter(ip_adress=param).afirst()
        else:
            logger.critical(f'param_for_search: {data_for_search}')
            raise ValueError

        if queryset:
            return data_for_search, model_to_dict(queryset, fields=[
                Database.FIELD_number.value, Database.FIELD_description.value, Database.FIELD_type_controller.value,
                Database.FIELD_ip_adress.value, Database.FIELD_address.value,
                # 'number', 'description', 'type_controller', 'ip_adress', 'address'
            ])
        return data_for_search, None

    async def get_queryset_traffic_lights(self, source: str, field: str) -> dict | None:
        """
        Поиск объекта в бд по номеру/ip-address
        :param data_for_search: кортеж вида (Номер СО/IP-address из http запроса, поле поска в бд)
        :return: кортеж вида (Номер СО/IP-address из http запроса, model_to_dict(queryset)) если объект найден,
                 иначе  (Номер СО/IP-address из http запроса, None)
        """

        if field == Database.FIELD_number.value:
            queryset = await TrafficLightsObjects.objects.filter(number=source).afirst()
        elif field == Database.FIELD_ip_adress.value:
            queryset = await TrafficLightsObjects.objects.filter(ip_adress=source).afirst()
        else:
            raise ValueError

        if queryset:
            return model_to_dict(queryset, fields=[
                Database.FIELD_number.value, Database.FIELD_description.value, Database.FIELD_type_controller.value,
                Database.FIELD_ip_adress.value, Database.FIELD_address.value,
            ])

    @classmethod
    async def get_queryset_chat_id_tg(cls, chat_id):
        queryset = await TelegrammUsers.objects.filter(chat_id=chat_id).afirst()
        if queryset:
            return model_to_dict(queryset)

    async def main(self, queryset_data: dict):
        """
        Главный метод, который собирает данные для запроса в бд для каждого хоста
        :param queryset_data:
        :return:
        """

        async with asyncio.TaskGroup() as tg:
            tasks_res = [
                tg.create_task(
                    self.get_queryset_traffic_lights(ipAddr_or_num, Database.FIELD_ip_adress.value
                    if ipAddr_or_num.count('.') == 3 else Database.FIELD_number.value),
                    name=ipAddr_or_num) for ipAddr_or_num in queryset_data
            ]
        logger.debug(tasks_res)
        return self.merge_queryset_data(queryset_data, tasks_res)

    def merge_queryset_data(self, data_hosts: dict, res_queryset: list[_asyncio.Task]) -> dict:
        """
        Метод объединяет данные, полученные из queryset с данными из data_host
        :param data_hosts: данные со всеми хостами
        :param res_queryset: результат запроса в бд
        :return: обновленный словарь со всеми хостами
        """

        for res in res_queryset:
            ipAddr_or_num, result = res.get_name(), res.result()
            if result is None:
                data_hosts[ipAddr_or_num][JsonResponceBody.REQ_ERRORS.value] = ErrorMessages.NUMBER_NOT_IN_DB.value
                continue
            ipAddr = result.get(JsonResponceBody.IP_ADDRESS.value)
            if not ipAddr:
                data_hosts[ipAddr_or_num][
                    JsonResponceBody.REQ_ERRORS.value] = ErrorMessages.IP_ADDRESS_NOT_FOUND_IN_DB.value
                continue
            data_hosts[ipAddr] = data_hosts[ipAddr_or_num] | result | {
                JsonResponceBody.HOST_ID.value: result.get(Database.FIELD_number.value),
                JsonResponceBody.HAS_IN_DB.value: True
            }
            for i, item in enumerate((ipAddr_or_num, JsonResponceBody.IP_ADDRESS.value, JsonResponceBody.NUMBER.value)):
                try:
                    if i == 0 and Checker.validate_err_ipv4(ipAddr_or_num) is not None:
                        del data_hosts[item]
                    else:
                        del data_hosts[ipAddr][item]
                    # data_hosts.pop(item) if i == 0 and Checker.validate_err_ipv4(ipAddr_or_num) is None else data_hosts[ipAddr].pop(item)
                except KeyError:
                    pass
        logger.debug(data_hosts)
        ResponceMaker.save_json_to_file(data_hosts, 'common.json')
        return data_hosts


class Checker:
    """
    Класс различных проверок валидности данных для выполения api запросов
    """

    def get_available_req_entities(self, type_req: str) -> set[str]:

        """
        Формирует множество с допустимыми типами запросов исходя из type_req(get или set)
        :param type_req: тип запроса из тела запроса, отправленного в api
        :return: если type_req принадлежит коллекции с get типами, возвращает множество get типов.
                 Если type_req принадлежит коллекции с set типами, возвращает множество типами команд
        """

        if type_req in AvailableTypesRequest.TYPE_GET.value:
            available_req_entities = {v.value for v in AvailableGetCommandsController}
        elif type_req in AvailableTypesRequest.TYPE_SET.value:
            available_req_entities = {v.value: None for v in AvailableSetCommandsController}
        else:
            raise ValueError
        return available_req_entities

    def check_error_request_in_all_hosts(self, data_hosts: dict) -> bool:
        """
        Проверяет что в data_hosts есть хотябы один хост без "request_errors" значения data_hosts[request_errors]: ...
        :param data_hosts: словарь с данными о хостах
        :return: Если есть хотябы один хост без request_errors -> возвращает False, иначе True
        """

        for ipAddr, data_host in data_hosts.items():
            if data_host == ErrorMessages.NUMBER_NOT_IN_DB.value:
                return True
            if not data_host.get('request_errors'):
                return False
        return True

    @classmethod
    def validate_err_ipv4(cls, ipV4: str) -> None | str:
        """
        Проверяет соответствует ip_addr строковому представлению IPv4/IPv6
        :param ipV4: проверяемая строка с IP-адрессом
        :return: None, если нет ошибки и переданная строка является IPv4, иначе строкое представление
                 о некоррктном IPV4
        """

        err_ipv4 = None
        try:
            ipaddress.ip_address(ipV4)
        except ValueError as err:
            err_ipv4 = err.__str__()
        except Exception as err:
            logger.warning(err)
        finally:
            return err_ipv4

    def validate_type_controller(self, type_controller: str) -> None | str:
        """
        Метод проверяет валидность типа контроллера
        :param type_controller: тип контроллера
        :return: None если нет ошибки, иначе текст ошибки
        """
        if (type_controller is None
                or type_controller.upper() not in {controller.value for controller in AvailableControllers}):
            return ErrorMessages.TYPE_CONTROLLER_NOT_PROVIDED.value

    def validate_req_entity_get_req(self, req_entity: list[str], available_req_entity: set) -> None | str:

        """
        Метод проверяет валидность req_entity для запросов типа get
        :param available_req_entity:
        :param req_entity: список с типом/типами запросов. Например: [get_config], [get_state]
        :return: None если нет ошибки, иначе текст ошибки
        """

        if not isinstance(req_entity, list):
            return ErrorMessages.INVALID_REQ_ENTITY.value
        for req in req_entity:
            if req not in available_req_entity:
                return ErrorMessages.INVALID_REQ_ENTITY.value

    def validate_req_entity_set_req(
            self, req_entity: dict[str, str], available_commands: set[str], type_controller: str
    ) -> None | str:
        """
        Метод проверяет валидность запрашиваемой команды и её значения
        :param type_controller: тип контроллера, для которого будет проводится проверка
        :param req_entity: словарь с типом команды и её значением. Например: {Фаза: 1}, {ЖМ: 1} и т.д.
        :param available_commands: множество, в котором сожержатся допустимые команды из AvailableSetCommandsController
        :return: None если команда и значение валидны иначе текст ошибки
        """

        if not isinstance(req_entity, dict):
            return ErrorMessages.INVALID_REQ_ENTITY.value
        type_command, set_val = list(req_entity.items())[0]
        type_command, set_val = type_command.upper(), set_val.upper()
        if type_command is None or type_command not in available_commands:
            return ErrorMessages.INVALID_COMMAND_TYPE.value
        return self.validate_val_command(type_controller.upper(), type_command, set_val)

    def validate_val_command(self, type_controller: str, type_command: str, set_val: str) -> None | str:
        """
        Метод проверяет валидность значения команды
        :param type_controller: тип контроллера
        :param type_command: тип команды (из AvailableSetCommandsController)
        :param set_val: проверяемое значение команды
        :return: None, если значение валидно, иначе текст ошибки
        """

        stage = 'ФАЗА'
        if (type_command == AvailableSetCommandsController.REBOOT.value
                or type_command == AvailableSetCommandsController.PROGRAM_RESTART.value):
            return
        if stage in type_command:
            if not set_val.isdigit():
                return ErrorMessages.INVALID_STAGE_VALUE.value
            if type_controller == AvailableControllers.SWARCO.value:
                if int(set_val) not in range(9):
                    return ErrorMessages.INVALID_STAGE_VALUE_FOR_THIS_TYPE_CONTROLLER.value
            else:
                if int(set_val) not in range(65):
                    return ErrorMessages.INVALID_STAGE_VALUE_FOR_THIS_TYPE_CONTROLLER.value
        else:
            if (type_command == AvailableSetCommandsController.USER_PARAMETERS.value
                    or type_command != AvailableSetCommandsController.INPUTS.value):
                return
            allowed_values = {
                'ВКЛ', 'ВЫКЛ', 'TRUE', 'FALSE', 'ON', 'OFF', '0', '1'
            }

            if set_val not in allowed_values:
                return ErrorMessages.INVALID_COMMAND_VALUE.value

    def validate_all_properties_data_hosts(self, data_hosts: dict, type_req: str) -> dict:
        """
        Метод реализует проверку обязательных данных добавление свойства request_errors(при необходимости),
        характерных для типа запроса(request_entity)
        :param type_req: тип запроса из тела запроса, отправленного в api
        :param data_hosts: словарь со свойствами всем хостов из запроса api
        :return: проверенный словарь со всеми хостами
        """

        logger.debug(type_req)
        available_req_entity = self.get_available_req_entities(type_req)

        for ipAddr, data_host in data_hosts.items():
            err_ipAddr = self.validate_err_ipv4(ipAddr)
            if err_ipAddr is not None:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = err_ipAddr
                continue
            type_controller = data_host.get(JsonResponceBody.TYPE_CONTROLLER.value)
            err_type_controller = self.validate_type_controller(type_controller)
            if err_type_controller is not None:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = err_type_controller
                continue

            if type_req in AvailableTypesRequest.TYPE_GET.value:
                err_req_entity = self.validate_req_entity_get_req(
                    data_host.get(JsonResponceBody.REQ_ENTITY.value), available_req_entity
                )
            else:
                err_req_entity = self.validate_req_entity_set_req(
                    data_host.get(JsonResponceBody.REQ_ENTITY.value), available_req_entity, type_controller
                )
            if err_req_entity is not None:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = err_req_entity
                continue
        return data_hosts


class ResponceMaker:
    """
    Класс формирует данные для ответа типа json для различных типов запросов
    """

    @classmethod
    def save_json_to_file(cls, json_data, file_name='data_hosts.json', mode: str = 'w') -> None:
        """
        Формирует json и записывает в файл
        :param json_data: словарь, который будет записан как json
        :param file_name: путь к файлу
        :param mode: режим записи в файл
        :return:
        """

        with open(file_name, mode, encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
            f.write('\n\n')

    @classmethod
    def merge_data_after_controller_management_req(cls, data_hosts: dict, res_req: list[_asyncio.Task]) -> dict:
        """
        Метод объединяет данные полученные после запроса с данными data_host
        :param data_hosts: словарь с данными всех хостов
        :param res_req: результат выполнения запроса
        :return: обновленные data_hosts
        """

        logger.debug(data_hosts)
        for res in res_req:
            ip = res.get_name()
            errInd, varBinds, obj = res.result()
            assert ip == obj.ip_adress
            if errInd:
                data_hosts[ip][JsonResponceBody.REQ_ERRORS.value] = errInd.__str__()
            else:
                json_from_controller_management = obj.create_json(errInd, varBinds)
                cls.save_json_to_file(json_from_controller_management, 'controller_management.json', mode='a')
                data_hosts[ip][JsonResponceBody.PROTOCOL.value] = (
                    json_from_controller_management.get(JsonResponceBody.PROTOCOL.value)
                )
                try:
                    (data_hosts[ip]
                    [JsonResponceBody.RESP_ENTITY.value]
                    [JsonResponceBody.RAW_DATA.value]) = (
                        json_from_controller_management[JsonResponceBody.RESP_ENTITY.value]
                        [JsonResponceBody.RAW_DATA.value]
                    )
                except KeyError:
                    pass
                try:
                    data_hosts[ip][JsonResponceBody.TIME_REQ_CONTROLLER.value] = (
                        json_from_controller_management[JsonResponceBody.TIME_REQ_CONTROLLER.value]
                    )
                except KeyError:
                    pass
                try:
                    data_hosts[ip][JsonResponceBody.REQUEST_EXEC_TIME.value] = (
                        int(time.time() - data_hosts[ip][JsonResponceBody.START_TIME.value])
                    )
                except KeyError:
                    pass

        return data_hosts

    @staticmethod
    def create_base_struct(data_hosts: dict) -> dict:
        """
        Метод создаёт общую структуру для json responce
        :param data_hosts: данные всех хостов из api запроса
        :return: словарь с созданными структурами для всех хостов из api запроса
        """
        logger.debug(data_hosts)

        for ipAddr, data_host in data_hosts.items():
            data_hosts[ipAddr] = {
                JsonResponceBody.START_TIME.value: int(time.time()),
                JsonResponceBody.REQ_ERRORS.value: data_host.get(JsonResponceBody.REQ_ERRORS.value),
                JsonResponceBody.HOST_ID.value: data_host.get(JsonResponceBody.HOST_ID.value),
                JsonResponceBody.PROTOCOL.value: data_host.get(JsonResponceBody.PROTOCOL.value),
                JsonResponceBody.VALID_DATA_REQUEST.value: data_host.get(JsonResponceBody.VALID_DATA_REQUEST.value),
                JsonResponceBody.TYPE_CONTROLLER.value: data_host.get(JsonResponceBody.TYPE_CONTROLLER.value),
                JsonResponceBody.ADDRESS.value: data_host.get(JsonResponceBody.ADDRESS.value),
                JsonResponceBody.TYPE.value: data_host.get(JsonResponceBody.TYPE.value),
                JsonResponceBody.REQUEST_EXEC_TIME.value: data_host.get(JsonResponceBody.REQUEST_EXEC_TIME.value),
                JsonResponceBody.REQ_ENTITY.value: data_host.get(JsonResponceBody.REQ_ENTITY.value),
                JsonResponceBody.RESP_ENTITY.value: {
                    JsonResponceBody.RAW_DATA.value: None
                }
            }
        logger.debug(data_hosts)
        return data_hosts

    @staticmethod
    def add_end_time_to_data_hosts(data_hosts: dict) -> dict:
        """
        Метод добавляет в json responce время, затраченное на выполение запроса
        :param data_hosts: данные всех хостов
        :param start_time: начало выполнения запроса а api
        :return: все хосты с добавленным свойством JsonResponceBody.REQUEST_EXEC_TIME.value
        """

        for ipAddr, _ in data_hosts.items():
            data_hosts[ipAddr][JsonResponceBody.REQUEST_EXEC_TIME.value] = (
                int(time.time() - data_hosts[ipAddr][JsonResponceBody.START_TIME.value])
            )
        return data_hosts

    def remove_prop(self, data_hosts: dict, remove_prop: tuple | list, add_exec_time: bool = True) -> dict:
        """
        Метод удаляет свойтва у каждого data_host из коллекции data_hosts
        :param data_hosts: данные всех хостов
        :param remove_prop: свойства из основного тела, которые необходимо удалить
        :param add_exec_time: рассчёт свойства JsonResponceBody.REQUEST_EXEC_TIME.value
        :return: обновлённая коллекция data_hosts
        """

        for ipAddr, _ in data_hosts.items():
            for prop in remove_prop:
                try:
                    del data_hosts[ipAddr][prop]
                except KeyError:
                    pass
            if add_exec_time:
                data_hosts[ipAddr][JsonResponceBody.REQUEST_EXEC_TIME.value] = (
                    int(time.time() - data_hosts[ipAddr][JsonResponceBody.START_TIME.value])
                )
        return data_hosts


class ControllerManagementBase:
    """
    Базовый класс управления контроллерами
    """

    def get_controller_obj(
            self, ip_adress: str, type_object: tuple, matches: dict, scn: str = None, host_id: str = None
    ):
        """
        Создает экземпляр класса на type_object для получения данных/управления контроллером
        :param matches: соответствия типа дк/типа команды своему классу
        :param ip_adress: ip дресс хоста
        :param type_object: кортеж вида (тип контроллера, тип запроса)
        :param scn: SCN контроллера, если необходимо задать вручную. Иначе бужет получен по snmp запросу
        :param host_id: id хоста для responce
        :return: экзмепляр соответствующего класса
        """

        obj = None
        try:
            obj = matches.get(type_object)(ip_adress, host_id)
            if 'scn' in obj.__dict__:
                obj.scn = scn or None
            logger.debug('try:')
        except TypeError:
            logger.debug('except TypeError %s:' % matches.get(type_object))
            obj = matches.get(type_object)(ip_adress, host_id)
        except Exception as err:
            logger.critical(err)
        finally:
            logger.info(obj)
            return obj


class GetDataFromController(ControllerManagementBase):
    """
    Класс получения данных о текущем состоянии контроллера
    """

    matches = {
        (AvailableControllers.SWARCO.value, 'get_state'):
            controller_management.SwarcoGetModeWeb,
        (AvailableControllers.PEEK.value, 'get_state'):
            controller_management.PeekGetModeWeb,
        (AvailableControllers.PEEK.value, 'get_states'):
            controller_management.GetDifferentStatesFromWeb,
        (AvailableControllers.POTOK_P.value, 'get_state'):
            controller_management.PotokP,
        (AvailableControllers.POTOK_S.value, 'get_state'):
            controller_management.PotokS,
    }

    async def main(self, data_hosts: dict) -> dict:
        """
        Главный метод для отправки запросов о состоянии хостов
        :param data_hosts: хосты с собранными данными
        :return: список завершённых задач
        """

        objects = []
        logger.debug(data_hosts)
        async with asyncio.TaskGroup() as tg:
            for ipAddr, data_host in data_hosts.items():
                logger.debug(data_host.get(JsonResponceBody.REQ_ENTITY.value))
                if data_host.get(JsonResponceBody.REQ_ERRORS.value):
                    continue
                scn = data_host.get(JsonResponceBody.SCN.value)
                type_controller = data_host.get(JsonResponceBody.TYPE_CONTROLLER.value)
                host_id = data_host.get(JsonResponceBody.HOST_ID.value)
                req_entity = data_host.get(JsonResponceBody.REQ_ENTITY.value)[0]
                obj = self.get_controller_obj(ipAddr, (type_controller.upper(), req_entity), self.matches, scn, host_id)
                if obj is None:
                    (data_hosts[ipAddr]
                    [JsonResponceBody.REQ_ERRORS.value]) = ErrorMessages.INVALID_CONTROLLER_TYPE_REQ.value
                    continue
                objects.append(obj)
            result_request = [
                tg.create_task(obj.get_request(get_mode=True), name=obj.ip_adress) for obj in objects
            ]

        data_hosts = ResponceMaker.merge_data_after_controller_management_req(data_hosts, result_request)
        logger.debug(data_hosts)
        return data_hosts


class SetRequestToController(ControllerManagementBase):
    """
    Класс управления дорожным контроллером
    """

    matches_controller_instance = {
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.FLASH_BUTTON.value):
            controller_management.AsyncPushButtonSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.DARK_BUTTON.value):
            controller_management.AsyncPushButtonSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.LOCAL_BUTTON.value):
            controller_management.AsyncPushButtonSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.FLASH_MAN.value):
            controller_management.AsyncSetInputsSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.DARK_MAN.value):
            controller_management.AsyncSetInputsSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.STAGE_MAN.value):
            controller_management.AsyncSetInputsSwarcoSSH,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.FLASH_SNMP.value):
            controller_management.SwarcoSTCIP,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.DARK_SNMP.value):
            controller_management.SwarcoSTCIP,
        (AvailableControllers.SWARCO.value, AvailableSetCommandsController.STAGE_SNMP.value):
            controller_management.SwarcoSTCIP,
        (AvailableControllers.POTOK_S.value, AvailableSetCommandsController.STAGE_SNMP.value):
            controller_management.PotokS,
        (AvailableControllers.POTOK_S.value, AvailableSetCommandsController.FLASH_SNMP.value):
            controller_management.PotokS,
        (AvailableControllers.POTOK_S.value, AvailableSetCommandsController.DARK_SNMP.value):
            controller_management.PotokS,
        (AvailableControllers.POTOK_S.value, AvailableSetCommandsController.PROGRAM_RESTART.value):
            controller_management.PotokS,
        (AvailableControllers.POTOK_P.value, AvailableSetCommandsController.STAGE_SNMP.value):
            controller_management.PotokP,
        (AvailableControllers.POTOK_P.value, AvailableSetCommandsController.FLASH_SNMP.value):
            controller_management.PotokP,
        (AvailableControllers.POTOK_P.value, AvailableSetCommandsController.DARK_SNMP.value):
            controller_management.PotokP,
        (AvailableControllers.POTOK_P.value, AvailableSetCommandsController.PROGRAM_RESTART.value):
            controller_management.PotokP,

        (AvailableControllers.PEEK.value, AvailableSetCommandsController.STAGE_MAN.value):
            controller_management.PeekSetInputsWeb,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.STAGE_SNMP.value):
            controller_management.PeekUG405,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.FLASH_MAN.value):
            controller_management.PeekSetInputsWeb,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.DARK_MAN.value):
            controller_management.PeekSetInputsWeb,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.CP_RED.value):
            controller_management.PeekSetInputsWeb,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.FLASH_MAN.value):
            controller_management.PeekSetInputsWeb,
        (AvailableControllers.PEEK.value, AvailableSetCommandsController.USER_PARAMETERS.value):
            controller_management.PeekSetUserParametersWeb,
    }

    matches_commands = {
        'ЖМ КНОПКА': AvailableSetCommandsController.FLASH_BUTTON.value,
        'ОС КНОПКА': AvailableSetCommandsController.DARK_BUTTON.value,
        'ЛОКАЛ КНОПКА': AvailableSetCommandsController.LOCAL_BUTTON.value,
        'ФАЗА MAN': AvailableSetCommandsController.STAGE_MAN.value,
        'ОС MAN': AvailableSetCommandsController.DARK_MAN.value,
        'ЖМ MAN': AvailableSetCommandsController.FLASH_MAN.value,
        'ОС SNMP': AvailableSetCommandsController.DARK_SNMP.value,
        'ЖМ SNMP': AvailableSetCommandsController.FLASH_SNMP.value,
        'ФАЗА SNMP': AvailableSetCommandsController.STAGE_SNMP.value,
        'КК CP_RED': AvailableSetCommandsController.CP_RED.value,
        'ПАРАМЕТРЫ ПРОГРАММЫ': AvailableSetCommandsController.USER_PARAMETERS.value,
        'РЕСТАРТ ПРОГРАММЫ': AvailableSetCommandsController.PROGRAM_RESTART.value,
        'ПЕРЕЗАГРУЗКА ДК': AvailableSetCommandsController.REBOOT.value
    }

    async def main(self, data_hosts: dict) -> dict:
        """
        Метод для отправки команд управления дорожным контроллером и сбора информации о запросе
        :param data_hosts: хосты с собранными данными
        :return: список завершённых задач
        """
        objects_methods = []
        logger.debug(data_hosts)
        for ipAddr, data in data_hosts.items():
            if data.get(JsonResponceBody.REQ_ERRORS.value):
                continue
            logger.debug(data)
            host_id = data.get(JsonResponceBody.HOST_ID.value)
            scn = data.get(JsonResponceBody.SCN.value)
            type_controller = data.get(JsonResponceBody.TYPE_CONTROLLER.value).upper()
            type_command, set_val = list(data.get(JsonResponceBody.REQ_ENTITY.value).items())[0]
            type_command = self.matches_commands.get(type_command.upper(), type_command.upper())
            obj = self.get_controller_obj(
                ipAddr, (type_controller.upper(), type_command), self.matches_controller_instance, scn, host_id
            )
            if obj is None:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = ErrorMessages.INVALID_CONTROLLER_TYPE_REQ.value
                continue
            method = self._get_method(obj, type_command, set_val)
            if method is not None:
                objects_methods.append((method, ipAddr))
            else:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = ErrorMessages.INVALID_COMMAND_TYPE.value

        if objects_methods:
            async with asyncio.TaskGroup() as tg:
                result_request = [tg.create_task(task, name=ipAddr) for task, ipAddr in objects_methods]
            logger.debug(f'result-->>> {result_request}')
        # data_hosts = self.get_raw_data_responce_entity(result_request, data_hosts)
        data_hosts = ResponceMaker.merge_data_after_controller_management_req(data_hosts, result_request)
        logger.debug(data_hosts)
        return data_hosts

    def _get_method(self, obj, type_command: str, set_val: str = None) -> Coroutine | None:

        set_stage = {AvailableSetCommandsController.STAGE_MAN.value, AvailableSetCommandsController.STAGE_SNMP.value}
        set_flash = {
            AvailableSetCommandsController.FLASH_MAN.value,
            AvailableSetCommandsController.FLASH_SNMP.value,
            AvailableSetCommandsController.FLASH_BUTTON.value
        }
        set_dark = {
            AvailableSetCommandsController.DARK_MAN.value,
            AvailableSetCommandsController.DARK_SNMP.value,
            AvailableSetCommandsController.DARK_BUTTON.value
        }
        all_red = {AvailableSetCommandsController.CP_RED.value}
        set_user_params_peek_web = AvailableSetCommandsController.USER_PARAMETERS.value
        set_restart_programm = AvailableSetCommandsController.PROGRAM_RESTART.value

        logger.debug(f'Команда: {type_command}, Значение: {set_val}')

        method = None
        if type_command in set_stage:
            method = obj.set_stage(set_val)
        elif type_command in set_flash:
            method = obj.set_flash(set_val)
        elif type_command in set_dark:
            method = obj.set_dark(set_val)
        elif type_command in all_red:
            method = obj.set_allred(set_val)
        elif type_command == set_restart_programm:
            method = obj.set_restart_program(set_val or '1')
        elif type_command == set_user_params_peek_web:
            method = obj.set_user_parameters(params_string=set_val)
        return method


class FileDownLoad:
    """
    Класс обслуживания загрузки файлов конфигурации контроллеров
    """

    swarco_config_path = os.getenv('path_to_itc_config_xml')

    @staticmethod
    def save_file_to_db(path: str, ipAddr: str, data: dict, source: str, description: str) -> SaveConfigFiles:
        """
        Метод сохранения файла конфигурации в бд
        :param description: описание источника сохранения файла
        :param source: назначение файла(created/uploaded)
        :param ipAddr: IPv4 хоста
        :param path: путь к конфигу(Swarco)/каталогу проекта(Peek)
        :param data: данные о хосте
        :return: None
        """

        f = SaveConfigFiles(source=source, file=path,
                            controller_type=data.get(JsonResponceBody.TYPE_CONTROLLER.value),
                            description=description,
                            address=data.get(JsonResponceBody.ADDRESS.value),
                            ip_adress=ipAddr,
                            number=data.get(JsonResponceBody.HOST_ID.value))
        f.file.name = correct_path_for_db(f.file.path)
        f.save()
        return f

    async def download_file(self, data_hosts: dict) -> dict:
        """
        Метод загрузки файла конфигурации с дорожного контроллера. Swarco -> scp, Peek -> ftp
        :param data_hosts: данные о хостах
        :return: результаты загрузки файла
        """

        logger.debug(data_hosts)
        obj_swarco_async, obj_peek_sync, result_async_request, result_sync_request = [], [], [], [],
        async with asyncio.TaskGroup() as tg:
            for ipAddr, data_host in data_hosts.items():
                if data_host.get(JsonResponceBody.REQ_ERRORS.value) is not None:
                    continue
                if data_host.get(JsonResponceBody.TYPE_CONTROLLER.value).upper() == AvailableControllers.SWARCO.value:
                    obj_swarco_async.append(controller_management.SwarcoSSHBase(ipAddr))
                elif data_host.get(JsonResponceBody.TYPE_CONTROLLER.value).upper() == AvailableControllers.PEEK.value:
                    # obj_peek_sync.append()... не реализовано
                    pass
                else:
                    continue
            if obj_swarco_async:
                data_hosts[ipAddr][JsonResponceBody.PROTOCOL.value] = JsonResponceBody.SSH.value
                result_async_request = [
                    tg.create_task(obj.adownload_scp(access_level='swarco_r',
                                                     files=[self.swarco_config_path],
                                                     dest_path=MEDIA_ROOT / 'uploaded_configs'),
                                   name=obj.ip_adress) for obj in obj_swarco_async
                ]

            if obj_peek_sync:
                # логика скачивания для Пика по ftp еще не реализована
                result_sync_request = []
            res = result_async_request + result_sync_request

        logger.debug(result_async_request)
        for data_host in res:
            errIndication, src, obj = data_host.result()
            if errIndication:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = errIndication
                continue
            if isinstance(obj, controller_management.SwarcoSSHBase):
                manager = controllers.SwarcoParseConfigXML(
                    f'{src}/{controllers.SwarcoParseConfigXML.xml_itc_config_name}'
                )
                errIndication, data = manager.create_PTC2(src)
                # data[0] -> path к конфигу, data[1] -> доп. сведения. В случае Swarco -> словарь с данными из
                # itc-config.xml "general"(кол-во групп, id_backplaine и т.д.)

                if errIndication:
                    data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = errIndication
                    continue
            else:
                data = [None, None]  # Заглушка
                pass  # Тут должно быть что то для Пика, возможно отдельный класс, в котором упаковываются файлы в архив
            data_hosts[obj.ip_adress][JsonResponceBody.DOWNLOAD_DATA.value] = data
        logger.debug(data_hosts)
        return data_hosts

    async def main(self, data_hosts: dict) -> dict:
        """
        Метод загрузки файла конфигурации с дорожного контроллера. Swarco -> scp, Peek -> ftp
        :param data_hosts: данные о хостах
        :return: результаты загрузки файла
        """

        logger.debug(data_hosts)
        obj_swarco_async, obj_peek_sync, result_async_request, result_sync_request = [], [], [], [],
        async with asyncio.TaskGroup() as tg:
            for ipAddr, data_host in data_hosts.items():
                if data_host.get(JsonResponceBody.REQ_ERRORS.value) is not None:
                    continue
                if data_host.get(JsonResponceBody.TYPE_CONTROLLER.value).upper() == AvailableControllers.SWARCO.value:
                    obj_swarco_async.append(controller_management.SwarcoSSHBase(ipAddr))
                elif data_host.get(JsonResponceBody.TYPE_CONTROLLER.value).upper() == AvailableControllers.PEEK.value:
                    # obj_peek_sync.append()... не реализовано
                    pass
                else:
                    continue
            if obj_swarco_async:
                data_hosts[ipAddr][JsonResponceBody.PROTOCOL.value] = JsonResponceBody.SSH.value
                result_async_request = [
                    tg.create_task(obj.adownload_scp(access_level='swarco_r',
                                                     files=[self.swarco_config_path],
                                                     dest_path=MEDIA_ROOT / 'uploaded_configs'),
                                   name=obj.ip_adress) for obj in obj_swarco_async
                ]

            if obj_peek_sync:
                # логика скачивания для Пика по ftp еще не реализована
                result_sync_request = []
            res = result_async_request + result_sync_request

        logger.debug(result_async_request)
        for data_host in res:
            errIndication, src, obj = data_host.result()
            if errIndication:
                data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = errIndication
                continue
            if isinstance(obj, controller_management.SwarcoSSHBase):
                manager = controllers.SwarcoParseConfigXML(
                    f'{src}/{controllers.SwarcoParseConfigXML.xml_itc_config_name}'
                )
                errIndication, data = manager.create_PTC2(src)
                # data[0] -> path к конфигу, data[1] -> доп. сведения. В случае Swarco -> словарь с данными из
                # itc-config.xml "general"(кол-во групп, id_backplaine и т.д.)

                if errIndication:
                    data_hosts[ipAddr][JsonResponceBody.REQ_ERRORS.value] = errIndication
                    continue
            else:
                data = [None, None]  # Заглушка
                pass  # Тут должно быть что то для Пика, возможно отдельный класс, в котором упаковываются файлы в архив
            data_hosts[obj.ip_adress][JsonResponceBody.DOWNLOAD_DATA.value] = data
        logger.debug(data_hosts)
        return data_hosts

    def make_zip_archive(self, path_to_config: str, ipAddr: str, host_id: str, type_controller: str) -> pathlib.Path:
        """
        Метод упаковывает в zip архив конфига/катлога проекта контроллера
        :param path_to_config: пусть к конфигу/каталогу проекта
        :param ipAddr: строковое представление ipv4 контроллера
        :param host_id: id контроллера(номер со/произвольное название)
        :param type_controller: тип контроллера: Swarco/Peek
        :return: Пусть к упакованному zip архиву
        """

        parent_dir = pathlib.Path('/'.join(path_to_config.split('/')[:-1]))
        path_for_send = pathlib.Path(f'{parent_dir}/for_send')
        os.makedirs(path_for_send)
        for file in parent_dir.iterdir():
            if not file.is_dir() and '.xml' not in file.name:
                shutil.copy(file, path_for_send)
        z_arch = pathlib.Path(f'{parent_dir}/{ipAddr} {host_id or ""}_{type_controller}.zip')
        with zipfile.ZipFile(z_arch, "w", zipfile.ZIP_DEFLATED) as z:
            for file in path_for_send.iterdir():
                if '.xml' not in file.name:
                    z.write(file, arcname=file.name)
        return z_arch

    def create_zip_archive_and_save_to_db_multiple(self, data_hosts: dict) -> dict:
        """
        Метод упаковывает скачанные конфиги/каталоги проектов и сохраняет их в бд, а также
        добавляет в словарь информацию о хосте
        :param data_hosts: словарь со всеми хостами
        :param res_download: результат загрузки
        :return: обновленный словарь с данными о хостах
        """
        logger.debug('create_zip_archive_and_save_to_db_multiple')

        for ipAddr, data_host in data_hosts.items():
            # data[0] -> path к конфигу, data[1] -> доп. сведения. В случае Swarco -> словарь с данными из
            # itc-config.xml "general"(кол-во групп, id_backplaine и т.д.)
            if data_hosts.get(ipAddr).get(JsonResponceBody.REQ_ERRORS.value) is not None:
                continue
            # data: список, где data[0] -> путь к скачанному(Peek)/созданному(Swarco .PTC2) файлу,
            # data[1] -> словарь полезных данных, в Swarco это general из xml
            path_to_file = data_host.get(JsonResponceBody.DOWNLOAD_DATA.value)[0]
            self.save_file_to_db(
                path_to_file, ipAddr, data_host, Database.CREATED.value, Database.DESCR_UPLOAD_CONFIG.value
            )
            res_make_zip = self.make_zip_archive(
                path_to_file, ipAddr,
                data_host.get(JsonResponceBody.HOST_ID.value),
                data_host.get(JsonResponceBody.TYPE_CONTROLLER.value)
            )
            # data_host[JsonResponceBody.PATH_TO_ARHIVE.value] = res_make_zip
            # saved_archive = self.save_file_to_db(str(res_make_zip), ipAddr, data_host)

            saved_archive = self.save_file_to_db(
                str(res_make_zip), ipAddr, data_host, Database.CREATED.value, Database.DESCR_CREATE_ARCHIVE.value
            )
            data_host[JsonResponceBody.RESP_ENTITY.value][JsonResponceBody.PATH_TO_URL.value] = {
                str(res_make_zip.name): saved_archive.file.url
            }
            data_host[JsonResponceBody.MODEL_OBJ.value] = saved_archive
            # data_host[JsonResponceBody.RESP_ENTITY.value][JsonResponceBody.PATH_TO_URL.value] = self.save_archive_to_db(
            #     res_make_zip, data_host
            # )
            (data_host[JsonResponceBody.RESP_ENTITY.value]
            [JsonResponceBody.RAW_DATA.value]) = data_host.get(JsonResponceBody.DOWNLOAD_DATA.value)[1]
            del data_host[JsonResponceBody.DOWNLOAD_DATA.value]
            # del data_host[JsonResponceBody.PATH_TO_ARHIVE.value]
            data_hosts[ipAddr] = data_host
        logger.debug(data_hosts)
        return data_hosts


class TelegrammBot:
    """
    Класс для работы с телеграмм ботом
    """

    token = os.getenv('SDP_BOT')
    send_document = 'sendDocument'
    send_message = 'sendDocument'

    def add_data_to_datahosts(self, data_hosts: dict, res_send_file: list[_asyncio.Task]) -> dict:
        """
        Метод собирает данные для responce в ответное сообщение пользователю telegramm, отправившему запрос
        :param data_hosts: данные с хостами
        :param res_send_file: результат с данными(заершённые задачи)
        :return: обновлённый словарь с данными о хостах
        """

        for res in res_send_file:
            logger.debug(res.result())
            ip = res.get_name()
            curr_host = data_hosts.get(ip)
            curr_host['responce_tlg'] = res.result()
            # del curr_host['obj']
        logger.debug(data_hosts)
        return data_hosts

    # def collect_data_for_responce(self, data_hosts: dict, res_send_file: list[_asyncio.Task]) -> dict:
    #     """
    #     Метод собирает данные для responce в ответное сообщение пользователю telegramm, отправившему запрос
    #     :param data_hosts: данные с хостами
    #     :param res_send_file: результат с данными(заершённые задачи)
    #     :return: обновлённый словарь с данными о хостах
    #     """
    #
    #     for res in res_send_file:
    #         logger.debug(res.result())
    #         ip = res.get_name()
    #         curr_host = data_hosts.get(ip)
    #         curr_host['responce_tlg'] = res.result()
    #         curr_host['protocol'] = 'ssh/ftp'
    #         del curr_host['path_to_archive']
    #         curr_host['raw_data_for_responce'] = {
    #             'intersection': curr_host.get('intersection'),
    #             'owner': curr_host.get('owner'),
    #             'controller-id': curr_host.get('controller-id'),
    #             'backplane-id': curr_host.get('backplane-id'),
    #         }
    #     logger.debug(data_hosts)
    #     return data_hosts

    async def send_request(self, chat_id: str, token=None, send_message=None, send_file=None, timeout=4) -> dict:
        """
        Отправка ответа пользователю отправившему запрос в telegramm через http запрос
        :param chat_id: чат id пользователя
        :param token: токен бота, по дефолту из env
        :param send_message: тип отправки -> сообщение
        :param send_file: тип отправки -> файл
        :param timeout: таймаут http сессии
        :return: telegramm json от http запроса
        """

        token = token or self.token
        if send_file:
            data = {'document': open(send_file, 'rb')}
            url = f'https://api.telegram.org/bot{token}/sendDocument?chat_id={chat_id}'
        elif send_message:
            url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}'
            data = {'parse_mode': 'MarkdownV2', 'text': send_message}
        else:
            raise ValueError('Не выбран тип запроса')

        timeout = aiohttp.ClientTimeout(timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=data) as s:
                return await s.json()

    async def send_file(self, chat_id: str, path_to_file: str, timeout=4, token: str = None) -> dict:
        """
        Метод отправляет файл пользователю отправившему запрос в telegramm через http запрос
        :param chat_id: чат id пользователя
        :param path_to_file: путь к zip архиву
        :param timeout: таймаут http сессии
        :param token: токен бота, по дефолту из env
        :return: telegramm json от http запроса
        """
        token = token or self.token
        res = await self.send_request(
            chat_id, token, send_file=path_to_file, timeout=timeout
        )
        return res

    async def send_message(self, chat_id: str, path_to_file, timeout=4, token=None):
        token = token or self.token
        logger.debug(chat_id, path_to_file)
        await self.send_request(
            chat_id, token, path_to_file,
        )

    async def main(
            self, data_hosts: dict, chat_id: str, send_message=None, send_file=None
    ) -> dict:
        """
        Метод групповой отправки ответного сообщения пользователю отправившему запрос в telegramm через http запрос
        :param chat_id:
        :param data_hosts: данные со всеми хостами
        :param send_message: тип отправки запроса текстовое сообщение
        :param send_file: тип отправки запроса файл
        :return: обновленные данные, готовые для json responce
        """

        logger.debug('---main----')
        async with asyncio.TaskGroup() as tg:
            res = [
                tg.create_task(
                    self.send_file(chat_id, data_host.get(JsonResponceBody.MODEL_OBJ.value).file.path),
                    name=ipAddr
                )
                for ipAddr, data_host in data_hosts.items() if data_host.get(JsonResponceBody.REQ_ERRORS.value) is None
            ]

        logger.debug(res)
        data_hosts = self.add_data_to_datahosts(data_hosts, res)
        logger.debug(data_hosts)
        return data_hosts


class CommonTables(metaclass=abc.ABCMeta):
    def __init__(self, raw_data_from_table: str, create_properties=False):
        self.raw_data = raw_data_from_table
        self.group_table = None
        self.stages_table = None
        self.num_groups = None
        if create_properties:
            self.create_properties()

    @abc.abstractmethod
    def create_properties(self):
        pass


class GroupTable(CommonTables):
    """
    Интерфейс преобразования сырых данных из "Таблицы направлений"
    в свойства направлений для сравнения с другими таблицами паспорта.
    """

    def create_properties(self):
        """
        Формирует свойства таблицы, необходимые для сравнения с таблицей фаз
        :return:
        """
        self.group_table = self._create_group_table(self.raw_data)
        self.num_groups = max(self.group_table)
        logger.debug(self.group_table)
        logger.debug(self.num_groups)

    def _create_group_table(self, data: str) -> Dict[int, Tuple[str, set]]:
        """
        Формирует словарь с отображением в каких фазах учатсвуют направления
        :param data: строка с данными о работе направлений в фазах
                     Пример data:
                                '1\tТранспортное\t1,2\n2\tТранспортное\t1,2,7\n3\tТранспортное\t4':

                                1	Транспортное	1,2
                                2	Транспортное	1,2,7
                                3	Транспортное	4

        :return: Словарь с отображением в каких фазах участвуют направления:
                {1: ('Транспортное', {1, 2}), 2: ('Транспортное', {1, 2, 7}), 3: ('Транспортное', {4})}


        """

        content_table_groups = (group.split('\t') for group in data.splitlines() if group)
        table_groups = {int(group[0]): [group[1], group[2].split(',')] for group in content_table_groups}
        for group in table_groups:
            name_group, stages = table_groups[group]
            try:
                table_groups[group] = name_group, set(stages)
            except ValueError:
                table_groups[group] = name_group, set(stages)
        return table_groups

    def create_stages_table(self):
        pass


class StagesTable(CommonTables):
    """
    Интерфейс преобразования сырых данных из "Программы(таблица фаз)"
    в свойства направлений для сравнения с другими таблицами паспорта.
    """

    def create_properties(self):
        """
        Формирует свойства таблицы, необходимые для сравнения с таблицей фаз
        :return:
        """

        self.stages_table = self._create_stage_table(self.raw_data)
        self.num_groups = max(functools.reduce(set.union, self.stages_table.values()))
        self.group_table = self._create_groups_table(self.stages_table, self.num_groups)

        logger.debug(self.stages_table)
        logger.debug(self.num_groups)
        logger.debug(self.group_table)

    def _create_stage_table(self, data: str) -> Dict[int, set]:

        table_stages = {}
        for stage_prop in data.splitlines():
            if not stage_prop:
                continue
            num_stage, groups_in_stage = stage_prop.split('\t')
            table_stages[num_stage] = set(map(int, groups_in_stage.split(',')))
        return table_stages

    def _create_groups_table(self, data: Dict[int, set], num_groups):

        table_groups = {k: set() for k in range(1, num_groups + 1)}
        for group in range(1, num_groups + 1):
            for stage, groups_in_stage in data.items():
                if group in groups_in_stage:
                    table_groups[group].add(stage)
        return table_groups


class Compares:
    """
    Интерфейс для сравнений различных данных
    """

    @classmethod
    def compare_groups_in_stages(cls, src_group_table: GroupTable, src_stages_table: StagesTable):
        resp = {}

        num_groups: int = max(set(src_group_table.group_table.keys()) | set(src_stages_table.group_table.keys()))
        resp['compare_num_groups'] = {
            'num_groups': num_groups,
            'ok': src_group_table.num_groups == src_group_table.num_groups == num_groups
        }
        logger.debug(resp)
        compare_groups_in_stages = {'ok': True}

        check_groups = {}
        for group in range(1, num_groups + 1):
            # logger.debug(group)
            # logger.debug(src_group_table.group_table[group][1])
            # logger.debug(src_stages_table.group_table[group])
            # logger.debug(src_group_table.group_table[group][1] ^ src_stages_table.group_table[group])

            discrepancy = src_group_table.group_table[group][1] ^ src_stages_table.group_table[group]
            if discrepancy:
                check_groups[group] = (
                    False if len(discrepancy) == 1 and any('красн' in w.lower() for w in discrepancy) else discrepancy
                )
            else:
                check_groups[group] = False
            if check_groups[group]:
                compare_groups_in_stages['ok'] = False

            logger.debug(check_groups)

        resp['compare_groups_in_stages'] = compare_groups_in_stages
        resp['compare_groups_in_stages']['groups_discrepancy'] = check_groups
        logger.debug(resp)
        return resp