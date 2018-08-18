# Generated by Django 2.0.7 on 2018-08-17 00:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('standings', '0036_auto_20180815_1439'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='season',
            options={'ordering': ['start_date']},
        ),
        migrations.AlterField(
            model_name='team',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='standings.Team'),
        ),
    ]
