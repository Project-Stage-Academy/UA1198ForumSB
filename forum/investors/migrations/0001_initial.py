<<<<<<< HEAD
# Generated by Django 5.0.6 on 2024-07-08 09:01
=======
# Generated by Django 5.0.6 on 2024-07-08 17:09
>>>>>>> 8037ddad579ec674c0d45b197b091f5618bfb524

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('investor_id', models.AutoField(primary_key=True, serialize=False)),
                ('investor_logo', models.BinaryField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('contacts', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Investor',
                'verbose_name_plural': 'Investors',
                'db_table': 'investor',
            },
        ),
    ]
