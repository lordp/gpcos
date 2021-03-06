# Generated by Django 2.0.4 on 2018-04-25 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('standings', '0023_auto_20180425_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_type', models.CharField(max_length=10)),
                ('lap_time', models.FloatField(default=0)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.Driver')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.Race')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.Season')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.Track')),
            ],
        ),
    ]
