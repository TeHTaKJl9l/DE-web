from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('request/new/', views.request_create, name='request_create'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('request/<int:pk>/edit/', views.request_update, name='request_update'),
    path('request/<int:pk>/delete/', views.request_delete, name='request_delete'),
    path('statistics/', views.statistics, name='statistics'),
    path('request/<int:pk>/extend/', views.extend_deadline, name='extend_deadline'),
    path('request/<int:pk>/qr/', views.generate_qr, name='generate_qr'),
]