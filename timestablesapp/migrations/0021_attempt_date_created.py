# Generated by Django 5.0 on 2023-12-18 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timestablesapp', '0020_remove_student_classes_student_classes'),
    ]

    operations = [
        migrations.AddField(
            model_name='attempt',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date Created'),
        ),
    ]
