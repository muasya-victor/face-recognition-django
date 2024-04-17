from django.contrib import admin
from .models import CustomUser, CapturedImage,RecognitionHistory


admin.site.register(CustomUser)
admin.site.register(RecognitionHistory)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']

@admin.register(CapturedImage)
class CapturedImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'image']
