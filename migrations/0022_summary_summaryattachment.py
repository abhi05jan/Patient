# Generated by Django 3.1.7 on 2021-04-09 05:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import patient.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_helpandsupport_investigations'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0021_auto_20210406_0712'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('deleted', models.BooleanField(blank=True, default=False, verbose_name='Delete')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('medical_history', models.TextField(blank=True, default='', null=True, verbose_name='Medical History')),
                ('doctor_note', models.TextField(blank=True, default='', null=True, verbose_name='Doctor Note')),
                ('blood_pressure', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Blood Pressure')),
                ('pulse_rate', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Pulse Rate')),
                ('temperature', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Temperature')),
                ('weight', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Weight')),
                ('blood_sugar', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Blood Sugar')),
                ('saturation', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Saturation')),
                ('respiratory_rate', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Respiratory Rate')),
                ('urinalysis', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Urinalysis')),
                ('impressions', models.TextField(blank=True, default='', null=True, verbose_name='Impressions')),
                ('plan', models.TextField(blank=True, default='', null=True, verbose_name='Plan')),
                ('prescriptions', models.TextField(blank=True, default='', null=True, verbose_name='Prescriptions')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctor_summary', to=settings.AUTH_USER_MODEL)),
                ('investigations', models.ManyToManyField(blank=True, related_name='investigations', to='account.Investigations')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_summary', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SummaryAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('deleted', models.BooleanField(blank=True, default=False, verbose_name='Delete')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('attachment', models.FileField(blank=True, null=True, upload_to=patient.models.patient_summary)),
                ('summary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachment_summary', to='patient.summary')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
    ]
