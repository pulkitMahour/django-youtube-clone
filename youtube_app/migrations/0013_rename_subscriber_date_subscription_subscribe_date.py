# Generated by Django 3.2.5 on 2022-02-04 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_app', '0012_auto_20220204_1836'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subscription',
            old_name='subscriber_date',
            new_name='subscribe_date',
        ),
    ]
