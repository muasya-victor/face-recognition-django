from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, CapturedImage,RecognitionHistory


admin.site.register(CustomUser)
admin.site.register(RecognitionHistory)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']

@admin.register(CapturedImage)
class CapturedImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']
