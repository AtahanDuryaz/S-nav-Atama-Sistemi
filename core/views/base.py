# Base Views - Temel imports ve yardımcı fonksiyonlar
"""
Tüm views dosyalarında kullanılacak ortak import'lar ve yardımcı fonksiyonlar
"""

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

# Python imports
import json
import logging
from datetime import datetime, timedelta

# Local imports
from ..models import (
    User, School, Faculty, Department, AssistantProfile,
    Course, Exam, ProctorAssignment, CalendarEvent
)
from ..forms import (
    CustomUserCreationForm, ExamCreationForm, 
    AssignmentForm, CalendarEventForm
)

# Logger setup
logger = logging.getLogger(__name__)

# Yetki kontrol fonksiyonları
def is_secretary(user):
    """Kullanıcının sekreter yetkisi olup olmadığını kontrol eder"""
    return user.has_secretary_permissions()

def is_assistant(user):
    """Kullanıcının asistan olup olmadığını kontrol eder"""
    return user.is_assistant()

def is_admin(user):
    """Kullanıcının admin olup olmadığını kontrol eder"""
    return user.role == 'ADMIN' or user.is_superuser
