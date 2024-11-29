
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from django.test import TestCase
from rest_framework.utils import json

from toolkit.models import TrafficLightObjects
from toolkit.serializers import TrafficLightsSerializer


# Create your tests_old here.


class TrafficLightTestCase(APITestCase):
    def test_get(self):
        obj1 = TrafficLightObjects.objects.create(
            num_CO='Test1',
            type_controller="Swarco",
            ip_adress='10.0.0.1',
            adress='Test adress',
            connection=True
        )

        obj2 = TrafficLightObjects.objects.create(
            num_CO='Test2',
            type_controller="Peek",
            ip_adress='10.0.0.2',
            adress='Test adress 2',
            connection=False
        )

        url = '/api/v1/traffilight_objects/'
        response = self.client.get(url)
        serializer_data = TrafficLightsSerializer([obj1, obj2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, list(reversed(response.data)))

# class LogicTestCase(TestCase):
#     print(f'LogicTestCase: LogicTestCase')
#     def t_func(self, x, y):
#         return x + y
#     def test_testov(self):
#         res = self.t_func(1, 4)
#         self.assertEqual(5, res)
