# Generated by Django 3.1.7 on 2021-03-26 11:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0011_auto_20210326_1059'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('deleted', models.BooleanField(blank=True, default=False, verbose_name='Delete')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('call_type', models.IntegerField(choices=[(1, 'Audio'), (2, 'Video')], default=1)),
                ('call_status', models.IntegerField(choices=[(1, 'Completed'), (2, 'Waiting'), (3, 'Not Attended'), (4, 'Pending'), (5, 'Accepted'), (6, 'Rejected')], default=2)),
                ('duration', models.IntegerField(default=0)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_call', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_call', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
