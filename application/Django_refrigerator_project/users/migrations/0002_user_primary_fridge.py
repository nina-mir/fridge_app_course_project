# Generated by Django 2.2.7 on 2019-11-14 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='primary_fridge',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]