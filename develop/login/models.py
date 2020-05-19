from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class User(models.Model):
    # id = models.UUIDField(primary_key=True, editable=False, default=uuid4,)
    username = models.CharField(max_length=8,default='admin')
    password = models.CharField(max_length=13,default = '13390924945')
    phone = models.CharField(max_length = 13,default='13390924945')


class Video(models.Model):
    methodpoi = (
    ('m1', 'model1'),
    ('m2', 'model2'),
    ('m3', 'model3'),
    )
    action_type = ((1,'kick'),(2,'daily'))
    state = ((1,'checked'),(2,'unchecked'))
    video_name = models.CharField(max_length=20,default='')
    introduction = models.CharField(max_length=20,default='')
    upload_time = models.DateField(default='2020-01-01')
    uploader = models.TextField(default='')
    # method = models.CharField(max_length = 10, choices=methodpoi,default='m1')
    # alarm_times = models.IntegerField(default='')
    # alarm_date = models.DateField(default='2020-01-01')
    # alarm_action = models.IntegerField(choices = action_type,default=1)
    # statement = models.IntegerField(choices = state,default=1)
    # position = models.FilePathField(path = 'video_image/')

