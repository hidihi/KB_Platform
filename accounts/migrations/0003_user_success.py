# Generated by Django 3.2.12 on 2022-05-18 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_my_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='success',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]