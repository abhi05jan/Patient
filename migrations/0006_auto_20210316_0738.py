# Generated by Django 3.1.7 on 2021-03-16 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0005_patientwaleet'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientWallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('deleted', models.BooleanField(blank=True, default=False, verbose_name='Delete')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('wallet', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patientwallet', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='PatientWaleet',
        ),
    ]
