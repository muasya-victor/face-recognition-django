from django.urls import path
from .views import capture_image, compare_images, login_view

urlpatterns = [
    path('capture/', capture_image, name='capture_image'),
    path('login/', login_view, name='login'),
    path('compare-images/', compare_images, name='compare_images'),
]
