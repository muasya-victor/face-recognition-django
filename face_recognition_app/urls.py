from django.urls import path
# from .views import compare_image, login_view, report
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.capture_image, name='capture_image'),
    path('login', views.login_view, name='login'),
    path('admin-report', views.login_history_view, name='admin_report'),
    path('admin', views.login_view, name='login'),
    path('report', views.generate_pdf_report, name ="generate_pdf_report"),
    path('', views.compare_image, name='compare_image'),
    path('user/<int:user_id>/', views.identified_user, name='identified_user'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
