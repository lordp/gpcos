# Generated by Django 2.0.4 on 2018-04-25 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('standings', '0021_seasonpenalty'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SortCriteria',
            new_name='SeasonStats',
        ),
    ]