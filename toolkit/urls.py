from django.conf.urls.static import static
from django.urls import path, re_path, register_converter, include
from rest_framework.routers import SimpleRouter

from engineering_tools import settings
from . import views
from . import converters
from .views import (
    ControllerManagementHostsConfigurationViewSetAPI,
    SearchByNumberTrafficLightsAPIView,
    ControllerManagementAPI,
    TrafficLightsUpdate, CompareGroups, CompareGroupsAPI
)


router = SimpleRouter()
router.register(r'controller-management-configurations', ControllerManagementHostsConfigurationViewSetAPI)

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path("login/", views.login, name='login'),
    path("contact/", views.contact, name='contact'),
    path("options/", views.options, name='options'),
    path("swarco/", views.controller_swarco, name='swarco'),
    path("peek/", views.controller_peek, name='peek'),
    path("potok/", views.controller_potok, name='potok'),
    path("about_controller/<int:post_id>/", views.show_tab, name='about_controller'),
    path("calc_cyc/", views.calc_cyc, name='calc_cyc'),

    path("calc_conflicts/", views.data_for_calc_conflicts, name='calc_conflicts'),
    path("manage_controllers/", views.ManageControllers.as_view(), name='manage_controllers'),
    path("download_config/", views.DownloadConfig.as_view(), name='download_config'),
    path("compare_groups/", views.CompareGroups.as_view(), name='compare_groups'),

    path("api/v1/", include(router.urls)),
    path("api/v1/manage-controller/", ControllerManagementAPI.as_view()),

    path("api/v1/download-config/", ControllerManagementAPI.as_view()),
    # path("api/v1/download-config-web/", DownloadFileFromControllerAPI.as_view()),

    path("api/v1/compare-groups/", CompareGroupsAPI.as_view()),

    path('api/v1/trafficlight-objects/<str:number>', SearchByNumberTrafficLightsAPIView.as_view()),
    path('api/v1/update_trafficlihgtdata/', TrafficLightsUpdate.as_view()),

    path(r'api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
# urlpatterns += router.urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
