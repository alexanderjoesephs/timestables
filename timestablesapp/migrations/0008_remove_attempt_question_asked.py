# Generated by Django 5.0 on 2023-12-12 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timestablesapp', '0007_attempt_question_asked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attempt',
            name='question_asked',
        ),
    ]