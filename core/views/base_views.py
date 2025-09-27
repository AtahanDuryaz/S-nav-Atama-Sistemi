# Base Views - Ana sayfa ve dashboard
"""
Temel views: Dashboard, ana sayfa vb.
"""

from .base import *

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
