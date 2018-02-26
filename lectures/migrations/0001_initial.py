# Generated by Django 2.0.2 on 2018-02-24 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('gps', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DayField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mon', models.BooleanField()),
                ('tue', models.BooleanField()),
                ('wed', models.BooleanField()),
                ('thu', models.BooleanField()),
                ('fri', models.BooleanField()),
                ('sat', models.BooleanField()),
                ('sun', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='lectures.Building')),
                ('days', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lectures.DayField')),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='YearAndSemester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField()),
                ('semester', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='lecture',
            name='professor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='lectures.Professor'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='year_and_semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='lectures.YearAndSemester'),
        ),
    ]
