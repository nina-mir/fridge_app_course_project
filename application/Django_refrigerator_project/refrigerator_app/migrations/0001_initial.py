# Generated by Django 2.2.7 on 2019-11-12 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fridge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('friends', models.TextField(blank=True, null=True)),
                ('auto_gen_grocery_list', models.TextField(blank=True, null=True)),
                ('manually_added_list', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateTimeField()),
                ('modified_date', models.DateTimeField()),
                ('eff_bgn_ts', models.DateTimeField()),
                ('eff_end_ts', models.DateTimeField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fridges', to='users.User')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('age', models.BigIntegerField(blank=True, null=True)),
                ('isperishable', models.IntegerField()),
                ('calories', models.IntegerField(blank=True, null=True)),
                ('creation_date', models.DateTimeField()),
                ('modified_date', models.DateTimeField()),
                ('eff_bgn_ts', models.DateTimeField()),
                ('eff_end_ts', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('sourceurl', models.TextField()),
                ('eff_bgn_ts', models.DateTimeField()),
                ('eff_end_ts', models.DateTimeField()),
                ('fridge', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipes', to='refrigerator_app.Fridge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipes', to='users.User')),
            ],
        ),
        migrations.CreateModel(
            name='FridgeContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expirationdate', models.DateTimeField()),
                ('size', models.IntegerField(blank=True, null=True)),
                ('creation_date', models.DateTimeField()),
                ('modified_date', models.DateTimeField()),
                ('eff_bgn_ts', models.DateTimeField()),
                ('eff_end_ts', models.DateTimeField()),
                ('addedby', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fridge_contents', to='users.User')),
                ('fridge', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fridge_contents', to='refrigerator_app.Fridge')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fridge_content', to='refrigerator_app.Item')),
            ],
        ),
    ]
