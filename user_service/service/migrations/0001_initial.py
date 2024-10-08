# Generated by Django 5.1.1 on 2024-09-23 22:02

import service.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[service.validators.validate_required])),
                ('email', models.CharField(unique=True, validators=[service.validators.validate_required])),
                ('address', models.CharField(validators=[service.validators.validate_required])),
                ('phone', models.CharField(unique=True, validators=[service.validators.validate_required])),
                ('password', models.CharField()),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
