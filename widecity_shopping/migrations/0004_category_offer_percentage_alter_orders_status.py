# Generated by Django 4.0.8 on 2022-10-18 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widecity_shopping', '0003_orders_payment_method_alter_orders_order_day_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='offer_percentage',
            field=models.CharField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(default='ordered', max_length=100),
        ),
    ]
