# Generated by Django 2.2.19 on 2022-11-27 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20221114_1906'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shoppingcart',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_cart'),
        ),
    ]