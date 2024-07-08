# Generated by Django 5.0.6 on 2024-07-08 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Startup',
            fields=[
                ('startup_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('location', models.CharField(blank=True, max_length=200, null=True)),
                ('startup_logo', models.BinaryField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contacts', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Startup',
                'verbose_name_plural': 'Startups',
                'db_table': 'startup',
            },
        ),
        migrations.CreateModel(
            name='StartupSize',
            fields=[
                ('size_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('people_count_min', models.IntegerField(default=0)),
                ('people_count_max', models.IntegerField()),
            ],
            options={
                'verbose_name': 'StartupSize',
                'verbose_name_plural': 'StartupSizes',
                'db_table': 'startup_size',
            },
        ),
    ]
