# Generated by Django 3.2 on 2022-02-09 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='yunlu_class_schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bjh', models.CharField(max_length=16)),
                ('week1', models.CharField(max_length=20)),
                ('week2', models.CharField(max_length=20)),
                ('week3', models.CharField(max_length=20)),
                ('week4', models.CharField(max_length=20)),
                ('week5', models.CharField(max_length=20)),
                ('week6', models.CharField(max_length=20)),
                ('week7', models.CharField(max_length=20)),
                ('week8', models.CharField(max_length=20)),
                ('week9', models.CharField(max_length=20)),
                ('week10', models.CharField(max_length=20)),
                ('week11', models.CharField(max_length=20)),
                ('week12', models.CharField(max_length=20)),
                ('week13', models.CharField(max_length=20)),
                ('week14', models.CharField(max_length=20)),
                ('week15', models.CharField(max_length=20)),
                ('week16', models.CharField(max_length=20)),
                ('week17', models.CharField(max_length=20)),
                ('week18', models.CharField(max_length=20)),
            ],
        ),
    ]