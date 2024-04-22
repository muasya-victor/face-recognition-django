# Generated by Django 5.0.2 on 2024-04-18 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_recognition_app', '0008_rename_image_capturedimage_captured_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='avatar',
            new_name='user_avatar',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='nationality',
            new_name='user_first_name',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='identification_number',
            new_name='user_identification_number',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='phone_code',
            new_name='user_phone_code',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='phone_number',
            new_name='user_phone_number',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_last_name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_nationality',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, default=1234, max_length=150, verbose_name='first name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
    ]