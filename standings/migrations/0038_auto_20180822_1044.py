# Generated by Django 2.0.7 on 2018-08-21 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standings', '0037_auto_20180817_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='qualifying_penalty_description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='result',
            name='race_penalty_description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
    ]