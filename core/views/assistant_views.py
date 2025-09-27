# Assistant Views - Asistan views'ları
"""
Asistanlar için özel views: Görev yönetimi, kabul/red işlemleri vb.
"""

from .base import *

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
