# Generated by Django 3.1.7 on 2021-03-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0009_planpurchasehistory_charge_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientpersonalprofile',
            name='other_lan',
            field=models.TextField(blank=True, null=True),
        ),
    ]