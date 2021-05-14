# Generated by Django 3.1.7 on 2021-03-27 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='slug',
            field=models.SlugField(allow_unicode=True, default='', unique=True),
        ),
        migrations.AddField(
            model_name='income',
            name='slug',
            field=models.SlugField(allow_unicode=True, default='', unique=True),
        ),
    ]
