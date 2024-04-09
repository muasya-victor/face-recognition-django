from django.urls import path
# from .views import compare_image, login_view, report
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.capture_image, name='capture_image'),
    path('login/', views.login_view, name='login'),
    path('report/', views.report, name= 'Admin  Report Page'),
    path('generate-report', views.generate_pdf, name ="Generate PDF"),
    path('compare/', views.compare_image, name='compare_image'),
    path('compare/result/', views.compare_image, name='compare_result'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
