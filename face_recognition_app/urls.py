from django.urls import path
# from .views import capture_image, compare_images, login_view
from . import views 
urlpatterns = [
    path('capture/', views.capture_image, name='capture_image'),
    path('login/', views.login_view, name='login'),
    path('compare-images/', views.compare_images, name='compare_images'),
    path('profile/', views.compare_with_user_profiles, name= 'compare_with_user_profiles')
]
