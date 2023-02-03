# Generated by Django 3.2.15 on 2022-09-07 13:54

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_fullctl", "0022_auto_20220907_1253"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceBridgeActionTask",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("django_fullctl.task",),
            managers=[
                ("handleref", django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name="servicebridgeaction",
            name="function",
            field=models.CharField(
                blank=True,
                choices=[
                    ("nautobot_push_device_loc", "Nautobot: update device location")
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
