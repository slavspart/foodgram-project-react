# Generated by Django 2.2.19 on 2022-09-08 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220908_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_surbscribed',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
