# Generated by Django 3.2.4 on 2021-08-05 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_fullctl", "0010_alter_managementtask_queue_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="managementtask",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("running", "Running"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=255,
            ),
        ),
    ]