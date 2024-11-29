from django.db import models
from django.utils import timezone

# Create your models here.


class SaveConfigFiles(models.Model):
    source = models.CharField(max_length=20)
    file = models.FileField(upload_to='conflicts/configs/', null=True, verbose_name='config_file')
    time_create = models.DateTimeField(default=timezone.now)
    controller_type = models.CharField(max_length=20, db_index=True, default='undefind')
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

