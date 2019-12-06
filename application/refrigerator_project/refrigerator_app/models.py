# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Fridge(models.Model):
    fridgeid = models.AutoField(db_column='FridgeID', primary_key=True)  # Field name made lowercase.
    fridgename = models.CharField(db_column='FridgeName', max_length=255)  # Field name made lowercase.
    owner = models.ForeignKey('Users', models.DO_NOTHING, db_column='Owner')  # Field name made lowercase.
    friends = models.TextField(db_column='Friends')  # Field name made lowercase.
    auto_gen_grocery_list = models.TextField(db_column='Auto_gen_grocery_list', blank=True, null=True)  # Field name made lowercase.
    manually_added_list = models.TextField(db_column='Manually_added_list', blank=True, null=True)  # Field name made lowercase.
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Fridge'


class FridgeContents(models.Model):
    fridgeid = models.ForeignKey(Fridge, models.DO_NOTHING, db_column='FridgeID')  # Field name made lowercase.
    itemid = models.ForeignKey('Items', models.DO_NOTHING, db_column='ItemID')  # Field name made lowercase.
    addedby = models.ForeignKey('Users', models.DO_NOTHING, db_column='AddedBy')  # Field name made lowercase.
    expirationdate = models.DateTimeField(db_column='ExpirationDate')  # Field name made lowercase.
    size = models.IntegerField(db_column='Size', blank=True, null=True)  # Field name made lowercase.
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Fridge_Contents'


class Items(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=255)  # Field name made lowercase.
    age = models.TimeField(db_column='Age')  # Field name made lowercase.
    isperishable = models.IntegerField(db_column='isPerishable')  # Field name made lowercase.
    calories = models.IntegerField(db_column='Calories', blank=True, null=True)  # Field name made lowercase.
    creation_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Items'


class Recipes(models.Model):
    fridgeid = models.ForeignKey(Fridge, models.DO_NOTHING, db_column='FridgeId')  # Field name made lowercase.
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='UserId')  # Field name made lowercase.
    title = models.TextField(db_column='Title')  # Field name made lowercase.
    sourceurl = models.TextField(db_column='SourceUrl')  # Field name made lowercase.
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Recipes'


class Users(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=255)  # Field name made lowercase.
    username = models.CharField(db_column='Username', unique=True, max_length=255)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    ownedfridges = models.TextField(db_column='OwnedFridges', blank=True, null=True)  # Field name made lowercase.
    friendedfridges = models.TextField(db_column='FriendedFridges', blank=True, null=True)  # Field name made lowercase.
    personalnotes = models.TextField(db_column='PersonalNotes', blank=True, null=True)  # Field name made lowercase.
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Users'
        unique_together = (('userid', 'email'),)
