from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from datetime import datetime


class CustomUser(AbstractUser):
    STUDENT = 'student'
    STAFF = 'staff'
    USER_TYPE_CHOICES = [
        (STUDENT, 'student'),
        (STAFF, 'staff'),
    ]
    
    user_phone_code = models.CharField(max_length=4, blank=True, null=True, default="+254")
    user_first_name = models.CharField(max_length=30, blank=True, null=True)
    user_last_name = models.CharField(max_length=30, blank=True, null=True)
    user_identification_number = models.CharField(max_length=50, unique=True)
    user_avatar = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default = 'student')
    user_phone_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    user_nationality = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return self.username
    

class CapturedImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    captured_image = models.ImageField(upload_to='captured_images/')
    

class RecognitionHistory(models.Model):
    recognition_image = models.ImageField(upload_to='review_image/', blank=True, null=True)
    recogntion_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__ (self):
        return f"{self.recognition_image} {self.recogntion_time}"
    

