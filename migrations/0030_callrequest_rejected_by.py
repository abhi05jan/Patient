# Generated by Django 3.1.7 on 2021-04-20 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0029_auto_20210419_0825'),
    ]

    operations = [
        migrations.AddField(
            model_name='callrequest',
            name='rejected_by',
            field=models.IntegerField(choices=[(1, 'Doctor'), (2, 'Patient'), (3, 'None')], default=3),
        ),
    ]
