# API Views - AJAX endpoints ve API fonksiyonları
"""
AJAX çağrıları ve API endpoints: Bölüm listeleri, auto-complete vb.
"""

from .base import *

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
def get_available_assistants(request):
    """
    Belirli bir tarih/saat için uygun asistanları getir (AJAX)
    """
    exam_datetime = request.GET.get('exam_datetime')
    exam_duration = request.GET.get('exam_duration', 2)  # varsayılan 2 saat
    
    if exam_datetime:
        try:
            # Tarih dönüştürme
            start_time = datetime.fromisoformat(exam_datetime)
            end_time = start_time + timedelta(hours=int(exam_duration))
            
            # Çakışan atamalar
            conflicting_assignments = ProctorAssignment.objects.filter(
                status='ACCEPTED',
                exam__exam_datetime__lt=end_time,
                exam__exam_end_time__gt=start_time
            ).values_list('assistant_id', flat=True)
            
            # Uygun asistanlar
            available_assistants = User.objects.filter(
                role='ASSISTANT',
                is_active=True
            ).exclude(id__in=conflicting_assignments).values(
                'id', 'first_name', 'last_name', 'email'
            )
            
            return JsonResponse(list(available_assistants), safe=False)
            
        except Exception as e:
            logger.error(f"Uygun asistanlar getirilirken hata: {str(e)}")
            return JsonResponse([], safe=False)
    
    return JsonResponse([], safe=False)


@login_required
@user_passes_test(is_secretary)
def get_exam_statistics(request):
    """
    Sınav istatistiklerini getir (Dashboard için)
    """
    try:
        # Bu hafta
        week_start = timezone.now().replace(hour=0, minute=0, second=0)
        week_end = week_start + timedelta(days=7)
        
        # Bu ay
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        stats = {
            'this_week': {
                'total_exams': Exam.objects.filter(
                    exam_datetime__range=[week_start, week_end]
                ).count(),
                'assigned_exams': Exam.objects.filter(
                    exam_datetime__range=[week_start, week_end],
                    proctorassignment__status='ACCEPTED'
                ).distinct().count(),
            },
            'this_month': {
                'total_exams': Exam.objects.filter(
                    exam_datetime__range=[month_start, month_end]
                ).count(),
                'completed_exams': Exam.objects.filter(
                    exam_datetime__range=[month_start, month_end],
                    exam_datetime__lt=timezone.now()
                ).count(),
            },
            'pending_assignments': ProctorAssignment.objects.filter(
                status='PENDING'
            ).count(),
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"İstatistikler getirilirken hata: {str(e)}")
        return JsonResponse({})


@login_required
@user_passes_test(is_assistant)
def get_my_schedule(request):
    """
    Asistanın kişisel programını getir (Takvim için)
    """
    try:
        # Tarih aralığı
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', ''))
            end_dt = datetime.fromisoformat(end_date.replace('Z', ''))
            
            # Kişisel etkinlikler
            events = CalendarEvent.objects.filter(
                assistant=request.user,
                start_datetime__range=[start_dt, end_dt]
            )
            
            # Kabul edilmiş görevler
            duties = ProctorAssignment.objects.filter(
                assistant=request.user,
                status='ACCEPTED',
                exam__exam_datetime__range=[start_dt, end_dt]
            ).select_related('exam__course')
            
            # JSON formatına dönüştür
            calendar_events = []
            
            # Etkinlikler
            for event in events:
                calendar_events.append({
                    'id': f'event_{event.id}',
                    'title': event.title,
                    'start': event.start_datetime.isoformat(),
                    'end': event.end_datetime.isoformat() if event.end_datetime else None,
                    'color': '#17a2b8',
                    'extendedProps': {'type': 'personal'}
                })
            
            # Görevler
            for duty in duties:
                calendar_events.append({
                    'id': f'duty_{duty.id}',
                    'title': f'Gözetmenlik: {duty.exam.course.course_code}',
                    'start': duty.exam.exam_datetime.isoformat(),
                    'end': duty.exam.exam_end_time.isoformat(),
                    'color': '#28a745',
                    'extendedProps': {'type': 'duty'}
                })
            
            return JsonResponse(calendar_events, safe=False)
            
    except Exception as e:
        logger.error(f"Program getirilirken hata: {str(e)}")
    
    return JsonResponse([])
