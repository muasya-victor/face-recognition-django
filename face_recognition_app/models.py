from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser



class CustomUser(models.Model):
    STUDENT = 'student'
    STAFF = 'staff'
    USER_TYPE_CHOICES = [
        (STUDENT, 'student'),
        (STAFF, 'staff'),
    ]
    email = models.EmailField(unique=True)
    phone_code = models.CharField(max_length=4, blank=True, null=True, default="+254")
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    identification_number = models.CharField(max_length=50, unique=True)
    avatar = models.FileField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default = 'student')
    username = models.CharField(max_length=128, unique=True, blank= True, null= True)
    password = models.CharField(max_length=128, default='123456')
    phone_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    nationality = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


class CapturedImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='captured_images/')
