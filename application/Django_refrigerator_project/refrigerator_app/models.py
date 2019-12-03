# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from users.models import User
from users.models import AuthUser
from django.db.models import IntegerField, Model, CharField
from django_mysql.models import ListTextField, ListCharField


class Fridge(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, models.DO_NOTHING, related_name='fridges')
    friends = ListTextField(base_field=IntegerField(), default=[])
    auto_gen_grocery_list = ListTextField(
        base_field=CharField(max_length=15), default=[])
    manually_added_list = ListTextField(
        base_field=CharField(max_length=15), default=[])
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()


class Item(models.Model):
    name = models.CharField(max_length=255)
    age = models.BigIntegerField(blank=True, null=True)
    isperishable = models.IntegerField()
    calories = models.IntegerField(blank=True, null=True)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()


class FridgeContent(models.Model):
    fridge = models.ForeignKey(
        Fridge, models.DO_NOTHING, related_name='fridge_contents')
    item = models.ForeignKey(Item, models.DO_NOTHING,
                             related_name='fridge_content')
    addedby = models.ForeignKey(
        User, models.DO_NOTHING, related_name='fridge_contents')
    expirationdate = models.DateTimeField()
    size = models.IntegerField(blank=True, null=True)
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()


class Recipe(models.Model):
    fridge = models.ForeignKey(
        Fridge, models.DO_NOTHING, related_name='recipes')
    user = models.ForeignKey(User, models.DO_NOTHING, related_name='recipes')
    title = models.TextField()
    sourceurl = models.TextField(null=True)
    imageurl = models.TextField(null=True)
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()
