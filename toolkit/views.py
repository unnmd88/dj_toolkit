import json
from io import BytesIO
import logging
import time
from datetime import datetime as dt

import asyncio
import openpyxl

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from engineering_tools.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from toolkit.models import SaveConfigFiles, SaveConflictsTXT, ControllerManagement, TrafficLightsObjects
from toolkit.sdp_lib import conflicts
from toolkit.serializers import ControllerHostsSerializer, BaseTrafficLightsSerializer
from . import services
from .constants import RequestOptions, AvailableTypesRequest

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
    Обновляет модель светофорных объектов
    """

    permission_classes = (IsAdminUser,)

    def post(self, request):
        start_time = time.time()
        logger.debug(request.FILES)
        file_in_memory = request.FILES['file'].read()
        wb = openpyxl.load_workbook(filename=BytesIO(file_in_memory))
        sh = wb.active

        all_obj = []
        for row_cells in sh.iter_rows():
            # num_co, addr, ip_addr, decsr, type_controller = row_cells
            num_co, type_controller, addr, description, ip_addr = row_cells

            num_co, addr, ip_addr, description, type_controller = num_co.value, addr.value, ip_addr.value, \
                description.value, type_controller.value

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
            group = matches_controllers_to_group.get(type_controller, 0)

            all_obj.append((
                TrafficLightsObjects(number=num_co, address=addr, description=description,
                                     ip_adress=ip_addr, type_controller=type_controller, group=group)
            ))
        TrafficLightsObjects.objects.all().delete()
        TrafficLightsObjects.objects.bulk_create(all_obj)
        logger.debug('Время обновления: %s' % (time.time() - start_time))
        return Response({'result': 'данные обновлены'})


class ControllerManagementAPI(APIView):
    """
    Управление/получение данных/загрузка конфига с контроллеров
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        start_time = time.time()
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
        logger.debug(request.data)
        data_body = request.data
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
        logger.debug(data_body)

        table_groups = services.GroupTable(data_body.get('content_table_groups'), create_properties=True)
        table_stages = services.StagesTable(data_body.get('content_table_stages'), create_properties=True)

        responce = services.Compares.compare_groups_in_stages(
            table_groups, table_stages
        )
        logger.debug(responce)


        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(responce)


""" CONFLICTS(UNSORTING...)  """


class ProcessedRequestBase:
    @staticmethod
    def reverse_slashes(path):
        path = path.replace('\\', '/')
        return path


class ProcessedRequestConflicts(ProcessedRequestBase):
    upload_name_id = 'upload_config_file'
    name_textarea = 'table_stages'
    controller_type = 'controller_type'

    @staticmethod
    def make_group_name(filename: str) -> str:
        """
        Возвращает id для модели UploadFiles2:
        swarco: swarco
        peek: peek
        остальные файлы: undefind
        :param filename: имя файла из коллекции request.FILEES:
        :return id_for_db -> имя группы(принадлежности)
        """
        if filename[-4:] == 'PTC2':
            id_for_db = 'swarco'
        elif filename[-3:] == 'DAT':
            id_for_db = 'peek'
        else:
            id_for_db = 'undefind'
        return id_for_db

    @staticmethod
    def correct_path(path):
        return ProcessedRequestBase.reverse_slashes(path).split('media/')[1]

    def __init__(self, request):
        self.request = request
        self.post_req_dict = request.POST.dict()
        self.files_dict = request.FILES.dict()
        self.controller_type = \
            self.post_req_dict.get(self.controller_type).lower() if self.controller_type in self.post_req_dict else None
        self.val_txt_conflicts = True if 'create_txt' in self.post_req_dict else False
        self.val_add_conflicts_and_binval_calcConflicts = True if 'binval_swarco' in self.post_req_dict else False
        self.val_make_config = True if 'make_config' in self.post_req_dict else False
        self.stages = self.post_req_dict.get(self.name_textarea)

        print('-' * 25)

        if request.FILES:
            if 'make_config' in self.post_req_dict:
                self.val_make_config = True
            if self.upload_name_id in self.files_dict:
                self.file_from_request = self.files_dict.get(self.upload_name_id)
                print(f'self.file_from_requestT: {self.file_from_request}')
                print(f'self.file_from_requestT: {type(self.file_from_request)}')
                print('--&&---')

                self.filename_from_request = self.file_from_request.name
                print(f'request.FILES.get(upload_name_id): {request.FILES.get(self.upload_name_id)}')
                print(f'request.FILES.get(upload_name_id): {type(request.FILES.get(self.upload_name_id))}')

                print(f'request.FILES2: {request.FILES}')
                print(f'self..file_from_request: {self.file_from_request}')
                print(f'self..filename_from_request: {self.filename_from_request}')
            self.group_name = self.make_group_name(filename=self.filename_from_request)
        else:
            self.val_make_config = False
            self.file_from_request = False
            self.filename_from_request = False

        # if self.val_txt_conflicts:
        #     self.make_txt_conflicts()
        #     self.path_to_txt_conflicts = SaveConflictsTXT.objects.last().file.path
        # else:
        #     self.path_to_txt_conflicts = None


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


def options(request):
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


def data_for_calc_conflicts(request):
    title = 'Расчёт конфликтов'

    if request.GET:
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}
        return render(request, 'toolkit/calc_conflicts.html', context=data)

    elif request.POST:
        req_data = ProcessedRequestConflicts(request)
        if req_data.val_make_config:
            SaveConfigFiles.objects.create(file=req_data.file_from_request, controller_type=req_data.group_name,
                                           source='uploaded', )
            path_to_config_file = SaveConfigFiles.objects.last().file.path
        else:
            path_to_config_file = None

    else:
        # DEBUG
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}
        return render(request, 'toolkit/calc_conflicts.html', context=data)

    print(f'BASE_DIR {BASE_DIR}')
    print(f'MEDIA_ROOT {MEDIA_ROOT}')
    print(f'MEDIA_URL {MEDIA_URL}')

    path_txt_conflict = f'{MEDIA_ROOT}/conflicts/txt/сalculated_conflicts {dt.now().strftime("%d %b %Y %H_%M_%S")}.txt'

    obj = conflicts.Conflicts()
    res, msg, *rest = obj.calculate_conflicts(
        input_stages=req_data.stages,
        controller_type=req_data.controller_type,
        make_txt_conflicts=req_data.val_txt_conflicts,
        add_conflicts_and_binval_calcConflicts=req_data.val_add_conflicts_and_binval_calcConflicts,
        make_config=req_data.val_make_config,
        prefix_for_new_config_file='new_',
        path_to_txt_conflicts=path_txt_conflict,
        path_to_config_file=path_to_config_file)

    print(f'res: {res}: msg {msg}')
    print(f'obj.result_make_config.: {obj.result_make_config}')
    print(f'obj.result_num_kolichestvo_napr: {obj.result_num_kolichestvo_napr}')
    print(f'sorted_stages: {obj.sorted_stages}')
    print(f'kolichestvo_napr: {obj.kolichestvo_napr}')
    print(f'matrix_output: {obj.matrix_output}')
    print(f'matrix_swarco_F997: {obj.matrix_swarco_F997}')
    print(f'conflict_groups_F992: {obj.conflict_groups_F992}')
    print(f'binary_val_swarco_for_write_PTC2: {obj.binary_val_swarco_for_write_PTC2}')
    print(f'binary_val_swarco_F009: {obj.binary_val_swarco_F009}')

    if obj.result_make_config and obj.result_make_config[0] and len(obj.result_make_config) >= 3:
        f = SaveConfigFiles(source='created', file=obj.result_make_config[2],
                            controller_type=req_data.group_name)
        f.file.name = ProcessedRequestConflicts.correct_path(f.file.path)
        f.save()
        create_link_config = True
    else:
        create_link_config = False

    if obj.result_make_txt and obj.result_make_txt[0] and len(obj.result_make_txt) >= 3:
        f = SaveConflictsTXT(source='created', file=obj.result_make_txt[2])
        f.file.name = ProcessedRequestConflicts.correct_path(f.file.path)
        f.save()
        create_link_txt_conflicts = True
    else:
        create_link_txt_conflicts = False

    data = {
        'menu_header': menu_header,
        'title': title,
        'render_conflicts_data': res,
        'add_conflicts_and_binval_calcConflicts': req_data.val_add_conflicts_and_binval_calcConflicts,
        'values': ('| K|', '| O|'),
        'matrix': obj.matrix_output,
        'sorted_stages': obj.sorted_stages,
        'kolichestvo_napr': obj.kolichestvo_napr,
        'matrix_swarco_F997': obj.matrix_swarco_F997,
        'conflict_groups_F992': obj.conflict_groups_F992,
        'binary_val_swarco_F009': obj.binary_val_swarco_F009,
        'create_link_txt_conflicts': create_link_txt_conflicts,
        'create_link_config': create_link_config,
        'txt_conflict_file': SaveConflictsTXT.objects.last() if SaveConflictsTXT.objects.last() else False,
        'config_file': SaveConfigFiles.objects.last() if SaveConfigFiles.objects.last() else False,
    }

    return render(request, 'toolkit/calc_conflicts.html', context=data)


def controller_swarco(request):
    data = {'title': 'Swarco', 'menu_header': menu_header}

    content = render_to_string('toolkit/swarco.html', data, request)

    return HttpResponse(content, )

    return render(request, 'toolkit/swarco.html', context=data, content_type='application/force-download')


def controller_peek(request):
    data = {'title': 'Peek', 'menu_header': menu_header}
    return render(request, 'toolkit/peek.html', context=data)


def controller_potok(request):
    data = {'title': 'Поток', 'menu_header': menu_header}
    return render(request, 'toolkit/potok.html', context=data)
