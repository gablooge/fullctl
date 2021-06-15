# Generated by Django 2.2.20 on 2021-06-03 05:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("django_fullctl", "0005_auto_20210528_1252"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="auditlog",
            name="org",
        ),
        migrations.AddField(
            model_name="auditlog",
            name="org_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="auditlog",
            name="org_object_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="auditlog_org_object_type_set",
                to="contenttypes.ContentType",
            ),
        ),
        migrations.AlterField(
            model_name="auditlog",
            name="object_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="auditlog_object_type_set",
                to="contenttypes.ContentType",
            ),
        ),
    ]
