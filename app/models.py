from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from .slugify import get_unique_slug
from cryptography.fernet import Fernet


# Create your models here.

class Income(models.Model):
    user = models.ForeignKey(User, related_name='user_income', on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, default=0, blank=False, decimal_places=2)
    amount = models.BinaryField(blank=True, default=b'amount')
    # description = models.TextField(blank=False, default='Incomes')
    description = models.BinaryField(blank=True, default=b'Income')
    datetime = models.DateTimeField(default=timezone.now, null=True)
    slug = models.SlugField(allow_unicode=True, unique=True, default='')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'datetime', 'slug')
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + " | " + str(self.datetime)

    class Meta:
        ordering = ['-datetime']


class Expense(models.Model):
    user = models.ForeignKey(User, related_name='user_expense', on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, default=0, blank=False, decimal_places=2)
    amount = models.BinaryField(blank=True, default=b'amount')
    # description = models.TextField(blank=False, default='Expense')
    description = models.BinaryField(blank=True, default=b'Expense')
    datetime = models.DateTimeField(default=timezone.now, null=True)
    slug = models.SlugField(allow_unicode=True, unique=True, default='')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'datetime', 'slug')
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + " | " + str(self.datetime)

    class Meta:
        ordering = ['-datetime']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    joined_on = models.DateTimeField(default=timezone.now)
    key = models.BinaryField(blank=True, default=b'')
    theme = models.TextField(default='null',blank=True)
    # key = models.TextField(blank=True, default='')


    def save(self, *args, **kwargs):
        if not self.key:
            self.key = Fernet.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return "@{}".format(self.user.username) + str(self.key)
