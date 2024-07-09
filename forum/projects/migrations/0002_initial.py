<<<<<<< HEAD
# Generated by Django 5.0.6 on 2024-07-08 09:01
=======
# Generated by Django 5.0.6 on 2024-07-08 17:09
>>>>>>> 8037ddad579ec674c0d45b197b091f5618bfb524

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investors', '0001_initial'),
        ('projects', '0001_initial'),
        ('startups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='startup',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='project', to='startups.startup'),
        ),
        migrations.AddField(
            model_name='industry',
            name='projects',
            field=models.ManyToManyField(related_name='industries', to='projects.project'),
        ),
        migrations.AddField(
<<<<<<< HEAD
=======
            model_name='project',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='projects.projectstatus'),
        ),
        migrations.AddField(
>>>>>>> 8037ddad579ec674c0d45b197b091f5618bfb524
            model_name='projectsubscription',
            name='investor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_subscriptions', to='investors.investor'),
        ),
        migrations.AddField(
            model_name='projectsubscription',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_subscriptions', to='projects.project'),
        ),
    ]
