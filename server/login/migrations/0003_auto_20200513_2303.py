# Generated by Django 2.2.12 on 2020-05-13 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20200513_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='alarm_action',
        ),
        migrations.RemoveField(
            model_name='video',
            name='alarm_date',
        ),
        migrations.RemoveField(
            model_name='video',
            name='alarm_times',
        ),
        migrations.RemoveField(
            model_name='video',
            name='method',
        ),
        migrations.RemoveField(
            model_name='video',
            name='statement',
        ),
    ]