# Generated by Django 3.1.7 on 2021-04-29 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0036_auto_20210427_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callrequest',
            name='call_status',
            field=models.IntegerField(choices=[(1, 'Completed'), (2, 'Waiting'), (3, 'Not Attended'), (4, 'Pending'), (5, 'Rejected'), (6, 'In Progress'), (7, 'Cancelled')], default=4),
        ),
    ]
