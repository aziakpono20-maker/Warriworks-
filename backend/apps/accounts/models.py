from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
 password=models.CharField(max_length=255,blank=True)
 class Role(models.TextChoices): CUSTOMER='customer','Customer'; ARTISAN='artisan','Artisan'; ADMIN='admin','Administrator'
 email=models.EmailField(unique=True)
 role=models.CharField(max_length=16,choices=Role.choices,default=Role.CUSTOMER)
 phone=models.CharField(max_length=24,blank=True)
 legacy_password_hash=models.CharField(max_length=255,blank=True)
 USERNAME_FIELD='email'; REQUIRED_FIELDS=['username']
 def __str__(self): return self.email
