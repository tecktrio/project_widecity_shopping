# Generated by Django 4.0.8 on 2022-10-17 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widecity_shopping', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='signup_day',
            field=models.CharField(default=17, max_length=50),
        ),
        migrations.AddField(
            model_name='users',
            name='signup_month',
            field=models.CharField(default=10, max_length=50),
        ),
        migrations.AddField(
            model_name='users',
            name='signup_year',
            field=models.CharField(default=2022, max_length=50),
        ),
        migrations.AlterField(
            model_name='orders',
            name='Order_day',
            field=models.CharField(default=17, max_length=100),
        ),
    ]