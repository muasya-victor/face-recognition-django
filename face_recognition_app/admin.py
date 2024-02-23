from django.contrib import admin
from .models import UserProfile, CapturedImage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']


# @admin.register(CapturedImage)
# class CapturedImageAdmin(admin.ModelAdmin):
#     list_display = ['user', 'image']
