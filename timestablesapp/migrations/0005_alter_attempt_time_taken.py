# Generated by Django 5.0 on 2023-12-12 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timestablesapp', '0004_attempt_time_taken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attempt',
            name='time_taken',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
