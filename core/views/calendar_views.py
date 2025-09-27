# Calendar Views - Takvim işlevleri
"""
Takvim yönetimi: Etkinlik ekleme, görüntüleme, silme vb.
"""

from .base import *

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
