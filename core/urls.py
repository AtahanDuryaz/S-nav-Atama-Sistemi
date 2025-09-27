# Core URL yapılandırması
from django.urls import path
from . import views

urlpatterns = [
    # Ana sayfa
    path('', views.dashboard, name='dashboard'),
    
    # Kimlik doğrulama
    path('auth/register/', views.register_view, name='register'),
    
    # Sınav yönetimi (Sekreterler için)
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    
    # Gözetmen atamaları
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/assign/', views.assign_proctor, name='assign_proctor'),
    
    # Asistan views
    path('duties/', views.my_duties, name='my_duties'),
    path('duties/<int:assignment_id>/accept/', views.duty_accept, name='duty_accept'),
    path('duties/<int:assignment_id>/reject/', views.duty_reject, name='duty_reject'),
    
    # Takvim işlevleri
    path('calendar/', views.my_calendar, name='my_calendar'),
    path('calendar/events/add/', views.add_calendar_event, name='add_calendar_event'),
    path('calendar/events/<int:event_id>/delete/', views.delete_calendar_event, name='delete_calendar_event'),
    
    # API endpoints
    path('api/departments/', views.get_departments_by_faculty, name='get_departments'),
]
