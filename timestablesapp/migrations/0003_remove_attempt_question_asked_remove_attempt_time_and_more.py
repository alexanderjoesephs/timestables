# Generated by Django 5.0 on 2023-12-12 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timestablesapp', '0002_attempt_correct_attempt_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attempt',
            name='question_asked',
        ),
        migrations.RemoveField(
            model_name='attempt',
            name='time',
        ),
        migrations.RemoveField(
            model_name='attempt',
            name='user_asked',
        ),
    ]
