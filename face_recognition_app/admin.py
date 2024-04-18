from django.contrib import admin
from .models import CustomUser, CapturedImage,RecognitionHistory


admin.site.register(CustomUser)
admin.site.register(RecognitionHistory)


@admin.register(CapturedImage)
class CapturedImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'captured_image']
