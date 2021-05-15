# Generated by Django 3.1.7 on 2021-04-27 07:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patient', '0034_labresult_call_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planpurchasehistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plan_purchase', to=settings.AUTH_USER_MODEL),
        ),
    ]
