# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'



class Fridge(models.Model):
    fridgeid = models.AutoField(db_column='FridgeID', primary_key=True)  # Field name made lowercase.
    fridgename = models.CharField(db_column='FridgeName', max_length=255)  # Field name made lowercase.
    owner = models.ForeignKey('Users', models.DO_NOTHING, db_column='Owner')  # Field name made lowercase.
    friends = models.TextField(db_column='Friends', null=True)  # Field name made lowercase.
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
    age = models.BigIntegerField(db_column='Age')  # Field name made lowercase.
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
    userid = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    username = models.CharField(db_column='Username', unique=True, max_length=255)  # Field name made lowercase.
    ownedfridges = models.TextField(db_column='OwnedFridges', blank=True, null=True)  # Field name made lowercase.
    friendedfridges = models.TextField(db_column='FriendedFridges', blank=True, null=True)  # Field name made lowercase.
    personalnotes = models.TextField(db_column='PersonalNotes', blank=True, null=True)  # Field name made lowercase.
    eff_bgn_ts = models.DateTimeField()
    eff_end_ts = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Users'
