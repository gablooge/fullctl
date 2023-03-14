# Generated by Django 3.2.16 on 2023-03-10 11:16

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django_handleref.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_fullctl', '0026_auto_20230131_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('source', models.CharField(max_length=255)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField()),
                ('http_status', models.PositiveIntegerField()),
                ('payload', models.JSONField(null=True)),
                ('count', models.PositiveIntegerField(default=1)),
                ('processing_error', models.CharField(blank=True, help_text='will hold error information if the request came back as a success but reading its data resulted in an error on our end.', max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Request',
                'verbose_name_plural': 'Requests',
                'db_table': 'request',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', django_handleref.models.CreatedDateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', django_handleref.models.UpdatedDateTimeField(auto_now=True, verbose_name='Updated')),
                ('version', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('ok', 'Ok'), ('pending', 'Pending'), ('deactivated', 'Deactivated'), ('failed', 'Failed'), ('expired', 'Expired')], default='ok', max_length=12)),
                ('source', models.CharField(max_length=255)),
                ('data', models.JSONField(null=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='response', to='django_fullctl.request')),
            ],
            options={
                'verbose_name': 'Response',
                'verbose_name_plural': 'Responses',
                'db_table': 'meta_response',
            },
            managers=[
                ('handleref', django.db.models.manager.Manager()),
            ],
        ),
    ]