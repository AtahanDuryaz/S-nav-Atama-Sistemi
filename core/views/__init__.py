# Views Package - Tüm view modüllerini burada import ediyoruz
"""
Core Views Paketi

Bu paket views'ları mantıklı gruplara ayırır:
- base_views.py: Temel views (dashboard, ana sayfa vb.)
- auth_views.py: Kimlik doğrulama views'ları 
- assistant_views.py: Asistan özel views'ları
- secretary_views.py: Sekreter views'ları
- calendar_views.py: Takvim işlevleri
- api_views.py: AJAX/API endpoints
"""

# Base views (dashboard vb.)
from .base_views import dashboard

# Kimlik doğrulama
from .auth_views import register_view

# Sekreter views
from .secretary_views import (
    exam_list, exam_create, exam_detail, 
    assign_proctor, assignment_list
)

# Asistan views  
from .assistant_views import (
    my_duties, duty_accept, duty_reject
)

# Takvim views
from .calendar_views import (
    my_calendar, add_calendar_event, delete_calendar_event
)

# API endpoints
from .api_views import get_departments_by_faculty

# Tüm views'ları __all__ listesinde tanımlıyoruz
__all__ = [
    # Base
    'dashboard',
    
    # Auth
    'register_view',
    
    # Secretary
    'exam_list', 'exam_create', 'exam_detail', 
    'assign_proctor', 'assignment_list',
    
    # Assistant
    'my_duties', 'duty_accept', 'duty_reject',
    
    # Calendar
    'my_calendar', 'add_calendar_event', 'delete_calendar_event',
    
    # API
    'get_departments_by_faculty',
]
