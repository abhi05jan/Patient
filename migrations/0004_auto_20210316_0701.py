# Generated by Django 3.1.7 on 2021-03-16 07:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminmanagement', '0002_auto_20210315_1006'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0003_auto_20210315_0836'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientmedicalehistory',
            name='wallet',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.CreateModel(
            name='PlanPurchaseHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('deleted', models.BooleanField(blank=True, default=False, verbose_name='Delete')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('card_number', models.CharField(default='', max_length=20)),
                ('card_name', models.CharField(default='', max_length=100)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminmanagement.planfeature')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
