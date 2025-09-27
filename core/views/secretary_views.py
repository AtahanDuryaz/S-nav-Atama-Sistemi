# Secretary Views - Sekreter views'ları
"""
Sekreterler için özel views: Sınav yönetimi, gözetmen atamaları vb.
"""

from .base import *

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
