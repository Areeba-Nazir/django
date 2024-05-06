from django.db import models
from django.contrib.auth.models import AbstractUser as authUser


# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=80, null=False, unique=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'auth_role'

    def __str__(self):
        return self.name


class User(authUser):
    """Creates auth_user table in the database."""
    email = models.EmailField(unique=True)
    active = models.BooleanField(null=True, default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    current_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=45, null=True, blank=True)
    current_login_ip = models.CharField(max_length=45, null=True, blank=True)
    login_count = models.IntegerField(null=True, default=0, blank=True)
    dict_status = models.TextField(default='on')
    login_from = models.TextField()
    conf_code = models.TextField(null=True, blank=True)
    temp_password = models.TextField(null=True, blank=True)
    reset_password_code = models.TextField(null=True, blank=True)
    subscription_status = models.CharField(max_length=25, default='free_mode')
    cus_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    user_status = models.TextField(default='ENABLED')
    roles = models.ManyToManyField(Role, blank=True)
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['id']
        db_table = 'auth_user'
        verbose_name = 'Auth User'

    def __repr__(self):
        """String representation of the class."""
        return "<email:%r, first_name:%r, lastname:%r, dict_status:%r, login_from:%r>" % (
            self.email, self.first_name, self.last_name, self.dict_status, self.login_from)

    def __str__(self):
        return self.email
