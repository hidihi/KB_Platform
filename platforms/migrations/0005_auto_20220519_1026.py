# Generated by Django 3.2.12 on 2022-05-19 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforms', '0004_auto_20220519_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=11, null=True),
        ),
        migrations.AlterField(
            model_name='trans',
            name='trans_price',
            field=models.DecimalField(decimal_places=5, max_digits=11),
        ),
    ]
