# Generated by Django 3.2.5 on 2022-02-03 05:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube_app', '0010_alter_userprofileinfo_cover_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='commenter_dp',
        ),
    ]