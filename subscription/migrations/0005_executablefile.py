# Generated by Django 5.2 on 2025-05-25 10:00

import subscription.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_plan_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutableFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=subscription.models.exe_upload_path)),
            ],
        ),
    ]
