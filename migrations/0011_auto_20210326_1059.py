# Generated by Django 3.1.7 on 2021-03-26 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0010_patientpersonalprofile_other_lan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientpersonalprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
