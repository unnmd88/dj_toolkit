import json
from io import BytesIO
import logging
import time
from datetime import datetime as dt

import asyncio
from typing import Generator

import openpyxl
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from openpyxl.cell import Cell
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets

import toolkit
from engineering_tools.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from toolkit.models import SaveConfigFiles, SaveConflictsTXT, ControllerManagement, TrafficLightsObjects
from toolkit.sdp_lib import conflicts_old, utils_common
from toolkit.serializers import ControllerHostsSerializer, BaseTrafficLightsSerializer
from . import services
from .constants import RequestOptions, AvailableTypesRequest
from django.core.exceptions import ObjectDoesNotExist


logger = logging.getLogger(__name__)

menu_header = [
    {'title': 'Главная страница', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
    {'title': 'Возможности', 'url_name': 'options'},
    {'title': 'Обратная связь', 'url_name': 'contact'},
    {'title': 'Вход', 'url_name': 'login'},
]

menu_common = [
    {'id': 1, 'title': 'Управление по SNMP', 'url_name': 'manage_controllers'},
    {'id': 3, 'title': 'Расчет цикла и сдвигов', 'url_name': 'calc_cyc'},
    {'id': 4, 'title': 'Расчет конфликтов', 'url_name': 'calc_conflicts'},
]

data_db2 = ['Управление контроллером', 'Фильтр SNMP',
            'Расчет цикла и сдвигов', 'Расчет конфликтов'
            ]

controllers_menu = [
    {'id': 1, 'title': 'Swarco', 'url_name': 'swarco'},
    {'id': 3, 'title': 'Peek', 'url_name': 'peek'},
    {'id': 4, 'title': 'Поток', 'url_name': 'potok'},
]

TYPES_CONTROLLER = ['Swarco', 'Поток (S)', 'Поток (P)', 'Peek']

path_tmp = 'toolkit/tmp/'
path_uploads = 'toolkit/uploads/'


def reverse_slashes(path):
    path = path.replace('\\', '/')
    return path


"""" API  """


class ControllerManagementHostsConfigurationViewSetAPI(viewsets.ModelViewSet):
    """
    Обрабатывает конфигурации "зелёных улиц", в зависимости от типа http запроса
    """

    permission_classes = (IsAuthenticated,)
    queryset = ControllerManagement.objects.all()
    serializer_class = ControllerHostsSerializer
    lookup_field = 'name'


class SearchByNumberTrafficLightsAPIView(generics.RetrieveAPIView):
    """
    Реализует поиск объекта в бд по полю number.
    Поле number не обязательно может являеться числовым номером. например возможно значение "413-P"
    """

    permission_classes = (IsAuthenticated,)
    queryset = TrafficLightsObjects.objects.all()
    serializer_class = BaseTrafficLightsSerializer
    lookup_field = 'number'


class TrafficLightsUpdate(APIView):
    """
    Обновляет модель светофорных объектов.
    SQL, который сбрасывает счетчик авто-инкремента pk:
    ALTER SEQUENCE toolkit_trafficlightsobjects_id_seq RESTART WITH 1;
    """
    # permission_classes = (IsAdminUser,)

    FILENAME = 'List'
    ALLOWED_FILE_EXT = {'xls', 'xlsx'}

    ID               = 0
    NUMBER           = 1
    TYPE_CONTROLLER  = 2
    ADDRESS          = 3
    LONGITUDE        = 4
    LATITUDE         = 5
    REGION           = 6
    DESCRIPTION      = 7
    IP_ADDRESS       = 8

    bad_response = {
        'result': 'Некорректное имя файла и/или расширение, данные не обновлены',
        'ok': False
    }
    good_response ={
        'result': 'Данные обновлены',
        'ok': True
    }
    matches_controllers_to_group = {
        'Swarco': 1,
        'Peek': 2,
        'Поток (P)': 3,
        'Поток (S)': 4,
        'Сигнал (STCIP)': 5,
        'Сигнал (SXTP)': 6,
        'ДКС': 7,
        'ДКС (Старт)': 8,
        'ДКСТ': 9,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._request = None
        self.wb = None
        self.sheet = None

    def post(self, request):
        start_time = time.time()
        logger.debug(request.FILES)
        if not self.check_filename(request.FILES['file'].name):
            return Response(self.bad_response)
        self.wb = openpyxl.load_workbook(filename=BytesIO(request.FILES['file'].read()))
        self.sheet = self.wb.active

        TrafficLightsObjects.objects.all().delete()
        TrafficLightsObjects.objects.bulk_create(self.get_model_objects())
        logger.debug(f'Время обновления: {(time.time() - start_time)}')
        return Response(self.good_response)

    def get_model_objects(self) -> Generator:
        it = self.sheet.iter_rows()
        next(it) # Пропустить первую row, которая является шапкой excel таблицы
        return (
            TrafficLightsObjects(
                id=row_cells[self.ID].value,
                number=row_cells[self.NUMBER].value,
                address=row_cells[self.ADDRESS].value,
                description=row_cells[self.DESCRIPTION].value,
                ip_adress=row_cells[self.IP_ADDRESS].value,
                type_controller=row_cells[self.TYPE_CONTROLLER].value,
                group=self.matches_controllers_to_group.get(row_cells[self.TYPE_CONTROLLER].value, 0)
            )
            for row_cells in it
        )

    def check_filename(self, full_filename: str) -> bool:
        splitter = '.'
        _full_filename = full_filename.split(splitter)
        if len(_full_filename) < 2:
            return False
        name, _extension = splitter.join(_full_filename[:-1]), _full_filename[-1]
        if _extension not in self.ALLOWED_FILE_EXT or name != self.FILENAME:
            return False
        return True


class ControllerManagementAPI(APIView):
    """
    Управление/получение данных/загрузка конфига с контроллеров
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        start_time = time.time()
        print(f'request: {request.data}')
        print(f'request:')

        data_body = request.data
        logger.debug(data_body)
        data_hosts_body, type_req, req_from_telegramm, chat_id, search_in_db = (
            data_body.get(RequestOptions.hosts.value),
            data_body.get(RequestOptions.type_request.value),
            data_body.get(RequestOptions.request_from_telegramm.value),
            data_body.get(RequestOptions.chat_id.value),
            data_body.get(RequestOptions.search_in_db.value)
        )
        logger.debug(data_hosts_body)
        if (data_hosts_body is None or type_req is None or type_req not in
                AvailableTypesRequest.TYPE_GET.value | AvailableTypesRequest.TYPE_SET.value):
            return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})

        db = services.QuerysetToDB()
        if req_from_telegramm is not None:
            if chat_id is None:
                return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})
            chat_id_is_valid = asyncio.run(db.get_queryset_chat_id_tg(chat_id))
            if chat_id_is_valid is None:
                return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})

        responce_manager = services.ResponceMaker()
        checker = services.Checker()

        data_hosts = responce_manager.create_base_struct(data_hosts_body)
        logger.debug(data_hosts)

        if search_in_db:
            data_hosts = asyncio.run(db.main(data_hosts))
            logger.debug('data_hosts_for_req_after_req_to_db')
            logger.debug(data_hosts)
        else:
            data_hosts = data_hosts_body

        responce_manager.save_json_to_file(data_hosts, 'data_hosts_after_queryset.json')
        logger.debug(data_hosts)
        data_hosts = checker.validate_all_properties_data_hosts(data_hosts, type_req)
        logger.debug(data_hosts)
        if checker.check_error_request_in_all_hosts(data_hosts):
            return Response(data_hosts)
        controller_manager = services.get_controller_manager(type_req)
        if controller_manager is None:
            return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})

        data_hosts = asyncio.run(controller_manager.main(data_hosts))
        if type_req == RequestOptions.type_get_config.value:
            logger.debug(data_hosts)
            data_hosts = controller_manager.create_zip_archive_and_save_to_db_multiple(data_hosts)
            if checker.check_error_request_in_all_hosts(data_hosts):
                return Response(responce_manager.add_end_time_to_data_hosts(data_hosts))
            if req_from_telegramm:
                send_file_tg = services.TelegrammBot()
                data_hosts = asyncio.run(
                    send_file_tg.main(data_hosts, chat_id, send_file=True)
                )
            data_hosts = responce_manager.remove_prop(data_hosts, (services.JsonResponceBody.MODEL_OBJ.value,))
            logger.debug(data_hosts)

        responce_manager.save_json_to_file(data_hosts)
        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(data_hosts)


class DownloadFileFromControllerAPI(APIView):
    """
    Загружает конфиг, формирует zip архив и отдает клиенту(на веб)
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        start_time = time.time()
        logger.debug(request.source_data)
        data_body = request.source_data
        data_hosts_body, type_req, req_from_telegramm, chat_id, search_in_db = (
            data_body.get(RequestOptions.hosts.value),
            data_body.get(RequestOptions.type_request.value),
            data_body.get(RequestOptions.request_from_telegramm.value),
            data_body.get(RequestOptions.chat_id.value),
            data_body.get(RequestOptions.search_in_db.value)
        )
        logger.debug(data_hosts_body)

        if data_hosts_body is None or type_req is None:
            return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})

        db = services.QuerysetToDB()
        responce_manager = services.ResponceMaker()
        checker = services.Checker()

        if req_from_telegramm is not None:
            if chat_id is None:
                return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})
            chat_id_is_valid = asyncio.run(db.get_queryset_chat_id_tg(chat_id))
            if chat_id_is_valid is None:
                return Response({'detail': services.ErrorMessages.BAD_DATA_FOR_REQ.value})

        data_hosts = responce_manager.create_base_struct(data_hosts_body)

        if search_in_db:
            data_hosts = asyncio.run(db.main(data_hosts))
            logger.debug('data_hosts_for_req_after_req_to_db')
            logger.debug(data_hosts_body)

        data_hosts = checker.validate_all_properties_data_hosts(data_hosts)
        logger.debug(data_hosts)

        if services.check_error_request_in_all_hosts(data_hosts):
            return Response(responce_manager.add_end_time_to_data_hosts(data_hosts))

        manager = services.FileDownLoad()
        data_hosts = asyncio.run(manager.download_file(data_hosts))

        logger.debug(data_hosts)
        data_hosts = manager.create_zip_archive_and_save_to_db_multiple(data_hosts)

        if services.check_error_request_in_all_hosts(data_hosts):
            return Response(responce_manager.add_end_time_to_data_hosts(data_hosts))

        if req_from_telegramm:
            send_file_tg = services.TelegrammBot()
            data_hosts = asyncio.run(
                send_file_tg.main(data_hosts, chat_id, send_file=True)
            )
        data_hosts = responce_manager.remove_prop(data_hosts, (services.JsonResponceBody.MODEL_OBJ.value,))
        logger.debug(data_hosts)

        services.ResponceMaker.save_json_to_file(data_hosts)
        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(data_hosts)


class CompareGroupsAPI(APIView):
    """
    Управление/получение данных/загрузка конфига с контроллеров
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        start_time = time.time()
        data_body = request.data
        options = data_body.get('options', [])
        logger.debug(data_body)
        manager = services.PassportProcessing(
            data_body.get('content_table_groups'), data_body.get('content_table_stages')
        )
        responce = manager.get_result(options)
        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(responce)


class PotokTrafficLightsConfiguratorAPI(APIView):
    permission_classes = (IsAuthenticated,)

    get_functions_from_condition_string = 'get_functions_from_condition_string'
    get_condition_result = 'get_condition_result'
    condition = 'condition'

    def post(self, request):
        start_time = time.time()
        print(request)
        data_body = request.data
        utils_common.write_data_to_file(
            data_for_write=json.dumps(data_body, indent=4), filename='cond_string.json'
        )
        condition = data_body.get(self.condition)
        options = data_body.get('options')
        if options is None:
            return Response({'detail': 'Предоставлены некорректные данные для запроса'})
        option_get_functions_from_condition_string = options.get(self.get_functions_from_condition_string)
        option_get_condition_result = options.get(self.get_condition_result)

        if option_get_functions_from_condition_string:
            get_funcs = services.GetFunctionsPotokTrafficLightsConfigurator(condition)
            get_funcs.get_functions()
            responce = {
                'functions': get_funcs.functions,
                'errors': get_funcs.errors
            }
        elif option_get_condition_result:
            func_values = data_body.get('payload').get('get_condition_result').get('func_values')
            get_result_condition = services.GetResultCondition(condition, func_values)
            get_result_condition.get_condition_result()
            responce = {
                'result': get_result_condition.current_result,
                'errors': get_result_condition.errors
            }
        else:
            responce = {'detail': 'Предоставлены некорректные данные для запроса'}
        return Response(responce)


class ConflictsAndStagesAPI(APIView):
    """
    Управление/получение данных/загрузка конфига с контроллеров
    """

    # permission_classes = (IsAuthenticated,)

    def post(self, request):

        start_time = time.time()
        logger.debug(request.FILES)

        try:
            entity_req_data = json.loads(request.data['data'])
            stages = entity_req_data['stages']
            type_controller = entity_req_data['type_controller']
            create_txt = entity_req_data['create_txt']
            create_config = entity_req_data['create_config']
            swarco_vals = entity_req_data['swarco_vals']
            file: InMemoryUploadedFile | None = request.FILES.get('file')

        except KeyError:
            return Response({'detail': 'Предоставлены некорректные данные для запроса'})

        data = services.ConflictsAndStages(raw_stages_groups=stages, type_controller=type_controller, create_txt=create_txt, scr_original_config=file)
        if data.errors:
            return Response({'detail': data.errors})
        data.calculate()

        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(data.instance_data)


"""" TEMPLATE VIEWS  """


class ManageControllers(TemplateView):
    template_name = 'toolkit/manage_controllers.html'
    extra_context = {
        'first_row_settings': {
            'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'
        },
        'second_row_get': {
            'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК', 'label_data': 'Данные с ДК'
        },
        'third_row_set': {
            'set_btn': 'Отправить'
        },
        'num_hosts': [i for i in range(1, 31)],
        'title': 'Управление контроллером',
        'types_controllers': TYPES_CONTROLLER
    }


class DownloadConfig(TemplateView):
    template_name = 'toolkit/download_config.html'
    extra_context = {
        'title': 'Загрузка конфигурации ДК'
    }


class CompareGroups(TemplateView):
    template_name = 'toolkit/compare_groups.html'
    extra_context = {
        'title': 'Сравнить направления из папсорта'
    }


class PotokTrafficLightsConfigurator(TemplateView):
    template_name = 'toolkit/potok_tlc.html'
    extra_context = {
        'title': 'Поток Traffic Lights Configurator'
    }


class ConflictsAndStages(TemplateView):

    template_name = 'toolkit/calc_conflicts.html'
    extra_context = {
        'title': 'Расчёт конфликтов и фаз'
    }


def index(request):
    print('ind')

    data = {'title': 'Главная страница',
            'menu_header': menu_header,
            'menu2': data_db2,
            'menu_common': menu_common,
            'controllers_menu': controllers_menu,
            }
    return render(request, 'toolkit/index.html', context=data)


def about(request):
    return render(request, 'toolkit/about.html', {'title': 'О сайте', 'menu_header': menu_header})


def contact(request):
    return HttpResponse('Обратная связь')


def login(request):
    return HttpResponse('Авторизация')


def options_(request):
    return HttpResponse('Возможности')


def show_tab(request, post_id):
    print('1')
    controller = get_object_or_404(TrafficLightsObjects, pk=post_id)

    data = {
        'num_CO': controller.ip_adress,
        'menu': menu_header,
        'controller': controller,
        'cat_selected': 1,
    }

    return render(request, 'toolkit/about_controller.html', context=data)

    # return HttpResponse(f'Отображение вкладки с id = {post_id}')


def calc_cyc(request):
    data = {'title': 'Расчёт циклов и сдвигов', 'menu_header': menu_header}
    return render(request, 'toolkit/calc_cyc.html', context=data)


def upload_file(file):
    with open(f'{path_tmp}{file.name}', 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> Страница не найдена </h1>")


def controller_swarco(request):
    data = {'title': 'Swarco', 'menu_header': menu_header}

    content = render_to_string('toolkit/swarco.html', data, request)

    return HttpResponse(content, )


def controller_peek(request):
    data = {'title': 'Peek', 'menu_header': menu_header}
    return render(request, 'toolkit/peek.html', context=data)


def controller_potok(request):
    data = {'title': 'Поток', 'menu_header': menu_header}
    return render(request, 'toolkit/potok.html', context=data)
