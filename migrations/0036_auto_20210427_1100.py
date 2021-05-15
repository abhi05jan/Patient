# Generated by Django 3.1.7 on 2021-04-27 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_joinreferral'),
        ('patient', '0035_auto_20210427_0731'),
    ]

    operations = [
        migrations.AddField(
            model_name='callrequestnotification',
            name='referal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referal', to='account.joinreferral'),
        ),
        migrations.AlterField(
            model_name='callrequestnotification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'CALL REQUEST'), (2, 'CLINIC STATUS'), (3, 'FOLLOW'), (3, 'FOLLOW'), (4, 'Referral')], default=1),
        ),
    ]
