# Core Views - Ana iş mantığı burada
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging

from .models import (
    User, School, Faculty, Department, AssistantProfile,
    Course, Exam, ProctorAssignment, CalendarEvent
)
from .forms import (
    CustomUserCreationForm, ExamCreationForm, 
    AssignmentForm, CalendarEventForm
)

logger = logging.getLogger(__name__)

# Yetki kontrol fonksiyonları
def is_secretary(user):
    """Kullanıcının sekreter yetkisi olup olmadığını kontrol eder"""
    return user.has_secretary_permissions()

def is_assistant(user):
    """Kullanıcının asistan olup olmadığını kontrol eder"""
    return user.is_assistant()

# Ana sayfa ve dashboard
@login_required
def dashboard(request):
    """
    Ana sayfa - Kullanıcı rolüne göre farklı içerik gösterir
    """
    context = {
        'user': request.user
    }
    
    try:
        if request.user.has_secretary_permissions():
            # Sekreter dashboard'u için veriler
            
            # Temel istatistikler
            stats = {
                'total_exams': Exam.objects.count(),
                'completed_exams': Exam.objects.filter(
                    exam_datetime__lt=timezone.now()
                ).count(),
                'pending_exams': Exam.objects.filter(
                    exam_datetime__gte=timezone.now()
                ).count(),
                'total_assignments': ProctorAssignment.objects.count(),
            }
            
            # Yaklaşan sınavlar (gelecek 7 gün)
            upcoming_exams = Exam.objects.filter(
                exam_datetime__gte=timezone.now(),
                exam_datetime__lte=timezone.now() + timezone.timedelta(days=7)
            ).select_related('course').order_by('exam_datetime')[:5]
            
            # Bekleyen onaylar
            pending_assignments = ProctorAssignment.objects.filter(
                status='PENDING'
            ).select_related('assistant', 'exam__course').order_by('-assigned_at')[:5]
            
            context.update({
                'stats': stats,
                'upcoming_exams': upcoming_exams,
                'pending_assignments': pending_assignments,
            })
            
        elif request.user.is_assistant():
            # Asistan dashboard'u için veriler
            
            try:
                assistant_profile = request.user.assistantprofile
                context['assistant_profile'] = assistant_profile
            except AssistantProfile.DoesNotExist:
                # Asistan profilini oluştur
                assistant_profile = AssistantProfile.objects.create(user=request.user)
                context['assistant_profile'] = assistant_profile
            
            # Asistan istatistikleri
            assignments = ProctorAssignment.objects.filter(assistant=request.user)
            
            stats = {
                'total_duties': assignments.count(),
                'accepted_duties': assignments.filter(status='ACCEPTED').count(),
                'pending_duties': assignments.filter(status='PENDING').count(),
                'rejected_duties': assignments.filter(status='REJECTED').count(),
            }
            
            # Bekleyen görevler
            pending_duties = assignments.filter(
                status='PENDING'
            ).select_related('exam__course').order_by('exam__exam_datetime')
            
            # Yaklaşan görevler (kabul edilmiş)
            upcoming_duties = assignments.filter(
                status='ACCEPTED',
                exam__exam_datetime__gte=timezone.now()
            ).select_related('exam__course').order_by('exam__exam_datetime')[:5]
            
            context.update({
                'stats': stats,
                'pending_duties': pending_duties,
                'upcoming_duties': upcoming_duties,
            })
            
    except Exception as e:
        logger.error(f"Dashboard hata: {str(e)}")
        messages.error(request, "Dashboard yüklenirken bir hata oluştu.")
    
    return render(request, 'core/dashboard.html', context)


# Kimlik doğrulama views
def register_view(request):
    """
    Kullanıcı kayıt sayfası - Rol bazlı dinamik form
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Admin onayı bekliyor
                
                # Rol bazlı ek bilgiler
                role = user.role
                
                if role in ['SECRETARY_FACULTY', 'SECRETARY_DEPARTMENT']:
                    # Sekreterler için bölüm/fakülte ataması
                    department_id = request.POST.get('department')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            # Sekreter türüne göre yetki belirleme
                            if role == 'SECRETARY_FACULTY':
                                # Fakülte sekreteri - fakülte genelinde yetki
                                user.department = None  # Fakülte geneli için
                                user.faculty = department.faculty
                            else:  # SECRETARY_DEPARTMENT
                                # Bölüm sekreteri - sadece o bölüm
                                user.department = department
                                user.faculty = department.faculty
                        except Department.DoesNotExist:
                            messages.error(request, "Geçersiz bölüm seçimi.")
                            return render(request, 'auth/register.html', {
                                'form': form,
                                'faculties': Faculty.objects.all(),
                                'departments': Department.objects.select_related('faculty').all()
                            })
                    else:
                        messages.error(request, "Sekreterler için bölüm seçimi zorunludur.")
                        return render(request, 'auth/register.html', {
                            'form': form,
                            'faculties': Faculty.objects.all(),
                            'departments': Department.objects.select_related('faculty').all()
                        })
                
                user.save()
                
                # Asistan ise profil oluştur
                if role == 'ASSISTANT':
                    department_id = request.POST.get('department')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            profile_data = {
                                'user': user,
                                'department': department,
                                'phone_number': request.POST.get('phone_number', ''),
                                'office_location': request.POST.get('office_location', ''),
                                'max_weekly_hours': request.POST.get('max_weekly_hours', 20),
                            }
                            AssistantProfile.objects.create(**profile_data)
                        except Department.DoesNotExist:
                            messages.error(request, "Geçersiz bölüm seçimi.")
                            return render(request, 'auth/register.html', {
                                'form': form,
                                'faculties': Faculty.objects.all(),
                                'departments': Department.objects.select_related('faculty').all()
                            })
                    else:
                        messages.error(request, "Asistanlar için bölüm seçimi zorunludur.")
                        return render(request, 'auth/register.html', {
                            'form': form,
                            'faculties': Faculty.objects.all(),
                            'departments': Department.objects.select_related('faculty').all()
                        })
                
                messages.success(
                    request,
                    'Kayıt işleminiz başarıyla tamamlandı. Hesabınızın admin tarafından '
                    'onaylanmasını bekleyin. E-posta ile bilgilendirileceksiniz.'
                )
                logger.info(f"Yeni kullanıcı kaydı: {user.email} ({user.get_role_display()}) - Bölüm: {getattr(user, 'department', 'N/A')}")
                return redirect('login')
                
            except Exception as e:
                logger.error(f"Kayıt hatası: {str(e)}")
                messages.error(request, "Kayıt işlemi sırasında bir hata oluştu.")
        else:
            messages.error(request, "Lütfen formu doğru şekilde doldurun.")
    else:
        form = CustomUserCreationForm()
    
    # Form için gerekli veriler
    faculties = Faculty.objects.prefetch_related('departments').all()
    departments = Department.objects.select_related('faculty').all()
    
    return render(request, 'auth/register.html', {
        'form': form,
        'faculties': faculties,
        'departments': departments
    })


# Sınav yönetimi views (Sekreterler için)
@login_required
@user_passes_test(is_secretary)
def exam_list(request):
    """
    Sınav listesi - Sekreterler için
    """
    # Filtreleme ve arama
    exams = Exam.objects.select_related('course__department', 'creator').all()
    
    # Arama
    search = request.GET.get('search')
    if search:
        exams = exams.filter(
            Q(course__course_code__icontains=search) |
            Q(course__course_name__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Tarih filtresi
    date_filter = request.GET.get('date_filter')
    if date_filter == 'upcoming':
        exams = exams.filter(exam_datetime__gte=timezone.now())
    elif date_filter == 'past':
        exams = exams.filter(exam_datetime__lt=timezone.now())
    
    # Durum filtresi
    status_filter = request.GET.get('status_filter')
    if status_filter == 'incomplete':
        exams = exams.filter(
            proctorassignment__isnull=True
        ).distinct()
    elif status_filter == 'complete':
        exams = exams.annotate(
            assigned_count=Count('proctorassignment', filter=Q(proctorassignment__status='ACCEPTED'))
        ).filter(assigned_count__gte=F('proctor_needed_count'))
    
    # Sıralama
    exams = exams.order_by('-exam_datetime')
    
    # Sayfalama
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'date_filter': date_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/exam_list.html', context)


@login_required
@user_passes_test(is_secretary)
def exam_create(request):
    """
    Yeni sınav oluşturma
    """
    if request.method == 'POST':
        form = ExamCreationForm(request.POST)
        if form.is_valid():
            try:
                exam = form.save(commit=False)
                exam.creator = request.user
                exam.save()
                
                messages.success(request, f"Sınav başarıyla oluşturuldu: {exam}")
                logger.info(f"Yeni sınav oluşturuldu: {exam} - Oluşturan: {request.user}")
                
                return redirect('exam_detail', exam_id=exam.id)
                
            except Exception as e:
                logger.error(f"Sınav oluşturma hatası: {str(e)}")
                messages.error(request, "Sınav oluşturulurken bir hata oluştu.")
        else:
            messages.error(request, "Lütfen formu doğru şekilde doldurun.")
    else:
        form = ExamCreationForm()
    
    return render(request, 'core/exam_create.html', {'form': form})


@login_required
@user_passes_test(is_secretary)
def exam_detail(request, exam_id):
    """
    Sınav detayları ve gözetmen atamaları
    """
    exam = get_object_or_404(
        Exam.objects.select_related('course__department', 'creator'),
        id=exam_id
    )
    
    # Gözetmen atamaları
    assignments = ProctorAssignment.objects.filter(exam=exam).select_related('assistant')
    
    # Mevcut asistanlar
    available_assistants = User.objects.filter(
        role='ASSISTANT',
        is_active=True
    ).exclude(
        id__in=assignments.values_list('assistant_id', flat=True)
    )
    
    context = {
        'exam': exam,
        'assignments': assignments,
        'available_assistants': available_assistants,
    }
    
    return render(request, 'core/exam_detail.html', context)


# Gözetmen atama views
@login_required
@user_passes_test(is_secretary)
@require_POST
def assign_proctor(request):
    """
    Gözetmen ataması yapma (AJAX)
    """
    try:
        exam_id = request.POST.get('exam_id')
        assistant_id = request.POST.get('assistant_id')
        
        exam = get_object_or_404(Exam, id=exam_id)
        assistant = get_object_or_404(User, id=assistant_id, role='ASSISTANT')
        
        # Mevcut atama kontrolü
        if ProctorAssignment.objects.filter(exam=exam, assistant=assistant).exists():
            return JsonResponse({
                'success': False,
                'message': 'Bu asistan zaten bu sınava atanmış.'
            })
        
        # Çakışma kontrolü
        conflicting = ProctorAssignment.objects.filter(
            assistant=assistant,
            status='ACCEPTED',
            exam__exam_datetime__range=[
                exam.exam_datetime,
                exam.exam_end_time
            ]
        ).exists()
        
        if conflicting:
            return JsonResponse({
                'success': False,
                'message': 'Bu asistan aynı zamanda başka bir sınava atanmış.'
            })
        
        # Atama oluştur
        assignment = ProctorAssignment.objects.create(
            exam=exam,
            assistant=assistant,
            assigned_by=request.user
        )
        
        logger.info(f"Gözetmen ataması yapıldı: {assignment}")
        
        return JsonResponse({
            'success': True,
            'message': f'{assistant.full_name} başarıyla atandı.',
            'assignment_id': assignment.id
        })
        
    except Exception as e:
        logger.error(f"Atama hatası: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Atama yapılırken bir hata oluştu.'
        })


# Asistan views
@login_required
@user_passes_test(is_assistant)
def my_duties(request):
    """
    Asistanın görevleri
    """
    assignments = ProctorAssignment.objects.filter(
        assistant=request.user
    ).select_related('exam__course').order_by('-assigned_at')
    
    # Durum filtresi
    status_filter = request.GET.get('status')
    if status_filter:
        assignments = assignments.filter(status=status_filter)
    
    # Sayfalama
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': ProctorAssignment.STATUS_CHOICES,
    }
    
    return render(request, 'core/my_duties.html', context)


@login_required
@user_passes_test(is_assistant)
def duty_accept(request, assignment_id):
    """
    Görev atamasını kabul etme
    """
    assignment = get_object_or_404(
        ProctorAssignment,
        id=assignment_id,
        assistant=request.user,
        status='PENDING'
    )
    
    try:
        assignment.accept_assignment()
        messages.success(request, f"Görev başarıyla kabul edildi: {assignment.exam}")
        logger.info(f"Görev kabul edildi: {assignment}")
        
    except Exception as e:
        logger.error(f"Görev kabul hatası: {str(e)}")
        messages.error(request, "Görev kabul edilirken bir hata oluştu.")
    
    return redirect('dashboard')


@login_required
@user_passes_test(is_assistant)
@require_POST
def duty_reject(request, assignment_id):
    """
    Görev atamasını reddetme
    """
    assignment = get_object_or_404(
        ProctorAssignment,
        id=assignment_id,
        assistant=request.user,
        status='PENDING'
    )
    
    reason = request.POST.get('reason', '').strip()
    if not reason:
        messages.error(request, "Red nedeni belirtilmelidir.")
        return redirect('dashboard')
    
    try:
        assignment.reject_assignment(reason)
        messages.success(request, "Görev başarıyla reddedildi.")
        logger.info(f"Görev reddedildi: {assignment} - Sebep: {reason}")
        
    except Exception as e:
        logger.error(f"Görev red hatası: {str(e)}")
        messages.error(request, "Görev reddedilirken bir hata oluştu.")
    
    return redirect('dashboard')


@login_required
@user_passes_test(is_assistant)
def my_calendar(request):
    """
    Asistan takvimi - Kişisel etkinlikler ve sınav görevleri
    """
    # Takvim etkinlikleri
    events = CalendarEvent.objects.filter(
        assistant=request.user
    ).order_by('start_datetime')
    
    # Kabul edilen sınav görevleri
    accepted_duties = ProctorAssignment.objects.filter(
        assistant=request.user,
        status='ACCEPTED'
    ).select_related('exam__course')
    
    # Yaklaşan görevler (gelecek 7 gün)
    upcoming_duties = accepted_duties.filter(
        exam__exam_datetime__gte=timezone.now(),
        exam__exam_datetime__lte=timezone.now() + timezone.timedelta(days=7)
    ).order_by('exam__exam_datetime')
    
    # FullCalendar için JSON formatında etkinlikler
    calendar_events = []
    
    # Kişisel etkinlikler
    for event in events:
        # Etkinlik türüne göre renk belirleme
        color = '#17a2b8'  # Varsayılan mavi
        if event.event_type == 'LECTURE':
            color = '#17a2b8'  # Mavi
        elif event.event_type == 'LAB':
            color = '#20c997'  # Teal
        elif event.event_type == 'MEETING':
            color = '#ffc107'  # Sarı
        elif event.event_type == 'OFFICE_HOURS':
            color = '#fd7e14'  # Turuncu
        else:  # PERSONAL
            color = '#6c757d'  # Gri
            
        calendar_events.append({
            'id': f'event_{event.id}',
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat() if event.end_datetime else None,
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'type': 'personal',
                'location': event.location or '',
                'description': event.description or '',
                'event_type': event.get_event_type_display()
            }
        })
    
    # Sınav görevleri
    for duty in accepted_duties:
        calendar_events.append({
            'id': f'duty_{duty.id}',
            'title': f'Gözetmenlik: {duty.exam.course.course_code}',
            'start': duty.exam.exam_datetime.isoformat(),
            'end': duty.exam.exam_end_time.isoformat(),
            'backgroundColor': '#28a745',
            'borderColor': '#28a745',
            'extendedProps': {
                'type': 'duty',
                'location': duty.exam.location or '',
                'course': duty.exam.course.course_name,
                'description': f'{duty.exam.course.course_name} dersi sınavı gözetmenliği'
            }
        })
    
    context = {
        'events': events,
        'upcoming_duties': upcoming_duties,
        'calendar_events_json': json.dumps(calendar_events),
    }
    
    return render(request, 'core/my_calendar.html', context)


@login_required
@user_passes_test(is_assistant)
def add_calendar_event(request):
    """
    Yeni takvim etkinliği ekleme
    """
    if request.method == 'POST':
        try:
            # Form verilerini al
            title = request.POST.get('title', '').strip()
            event_type = request.POST.get('event_type')
            start_datetime = request.POST.get('start_datetime')
            end_datetime = request.POST.get('end_datetime')
            location = request.POST.get('location', '').strip()
            description = request.POST.get('description', '').strip()
            is_recurring = request.POST.get('is_recurring') == 'on'
            
            # Validation
            if not all([title, event_type, start_datetime]):
                messages.error(request, "Başlık, tür ve başlangıç tarihi zorunludur.")
                return redirect('my_calendar')
            
            # Tarih dönüştürme
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_datetime)
            end_dt = None
            if end_datetime:
                end_dt = datetime.fromisoformat(end_datetime)
                
                # Bitiş tarihi kontrolü
                if end_dt <= start_dt:
                    messages.error(request, "Bitiş tarihi başlangıç tarihinden sonra olmalıdır.")
                    return redirect('my_calendar')
            
            # Çakışma kontrolü (opsiyonel)
            conflicting_events = CalendarEvent.objects.filter(
                assistant=request.user,
                start_datetime__lt=end_dt or start_dt,
                end_datetime__gt=start_dt
            )
            
            if conflicting_events.exists():
                messages.warning(
                    request, 
                    "Bu zaman diliminde başka bir etkinliğiniz var. "
                    "Devam etmek istiyorsanız takvimi kontrol edin."
                )
            
            # Etkinliği oluştur
            event = CalendarEvent.objects.create(
                assistant=request.user,
                title=title,
                event_type=event_type,
                start_datetime=start_dt,
                end_datetime=end_dt,
                location=location,
                description=description,
                is_recurring=is_recurring
            )
            
            messages.success(request, f"Etkinlik başarıyla eklendi: {title}")
            logger.info(f"Yeni etkinlik eklendi: {event} - Asistan: {request.user}")
            
        except ValueError as e:
            logger.error(f"Tarih format hatası: {str(e)}")
            messages.error(request, "Geçersiz tarih formatı.")
        except Exception as e:
            logger.error(f"Etkinlik ekleme hatası: {str(e)}")
            messages.error(request, "Etkinlik eklenirken bir hata oluştu.")
    
    return redirect('my_calendar')


@login_required
@user_passes_test(is_assistant)
@require_POST
def delete_calendar_event(request, event_id):
    """
    Takvim etkinliğini silme (AJAX)
    """
    try:
        event = get_object_or_404(
            CalendarEvent, 
            id=event_id, 
            assistant=request.user
        )
        
        event_title = event.title
        event.delete()
        
        logger.info(f"Etkinlik silindi: {event_title} - Asistan: {request.user}")
        
        return JsonResponse({
            'success': True,
            'message': f'{event_title} başarıyla silindi.'
        })
        
    except Exception as e:
        logger.error(f"Etkinlik silme hatası: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Etkinlik silinirken bir hata oluştu.'
        })


# API endpoints (AJAX için)
@login_required
def get_departments_by_faculty(request):
    """
    Fakülteye göre bölümleri getir (AJAX)
    """
    faculty_id = request.GET.get('faculty_id')
    if faculty_id:
        try:
            departments = Department.objects.filter(
                faculty_id=faculty_id
            ).values('id', 'name').order_by('name')
            return JsonResponse(list(departments), safe=False)
        except Exception as e:
            logger.error(f"Bölümler getirilirken hata: {str(e)}")
            return JsonResponse([], safe=False)
    return JsonResponse([], safe=False)


@login_required
@user_passes_test(is_secretary)
def assignment_list(request):
    """
    Gözetmen atamalarının listesi
    """
    assignments = ProctorAssignment.objects.select_related(
        'assistant', 'exam__course', 'assigned_by'
    ).all()
    
    # Filtreleme
    search = request.GET.get('search')
    if search:
        assignments = assignments.filter(
            Q(assistant__first_name__icontains=search) |
            Q(assistant__last_name__icontains=search) |
            Q(exam__course__course_code__icontains=search)
        )
    
    status_filter = request.GET.get('status')
    if status_filter:
        assignments = assignments.filter(status=status_filter)
    
    # Sıralama
    assignments = assignments.order_by('-assigned_at')
    
    # Sayfalama
    paginator = Paginator(assignments, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'status_choices': ProctorAssignment.STATUS_CHOICES,
    }
    
    return render(request, 'core/assignment_list.html', context)
