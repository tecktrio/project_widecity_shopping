# Generated by Django 4.0.8 on 2022-10-21 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widecity_shopping', '0010_users_reference_id_alter_orders_order_day_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='References',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('refered_user_id', models.CharField(max_length=100)),
            ],
        ),
    ]
