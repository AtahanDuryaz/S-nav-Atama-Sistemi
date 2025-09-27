# Django Admin Panel Konfigürasyonu
# Bu dosya, admin panelinde modellerin nasıl görüneceğini ve yönetileceğini belirler.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, School, Faculty, Department, AssistantProfile,
    Course, Exam, ProctorAssignment, CalendarEvent
)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Özel User modeli için admin konfigürasyonu
    """
    # Listeleme sayfasında görünecek alanlar
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)
    
    # Detay sayfasındaki alanların gruplandırılması
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('email', 'username', 'password')
        }),
        ('Kişisel Bilgiler', {
            'fields': ('first_name', 'last_name')
        }),
        ('Yetki ve Rol', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Önemli Tarihler', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Grup ve İzinler', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)  # Varsayılan olarak kapalı
        }),
    )
    
    # Yeni kullanıcı ekleme formu
    add_fieldsets = (
        ('Temel Bilgiler', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Kişisel Bilgiler', {
            'fields': ('first_name', 'last_name')
        }),
        ('Rol', {
            'fields': ('role',)
        }),
    )
    
    # Admin eylemları
    actions = ['approve_users', 'deactivate_users']
    
    def approve_users(self, request, queryset):
        """Seçili kullanıcıları onaylar"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} kullanıcı onaylandı.')
    approve_users.short_description = "Seçili kullanıcıları onayla"
    
    def deactivate_users(self, request, queryset):
        """Seçili kullanıcıları deaktif eder"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} kullanıcı deaktif edildi.')
    deactivate_users.short_description = "Seçili kullanıcıları deaktif et"


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """
    Okul modeli için admin konfigürasyonu
    """
    list_display = ('name', 'faculty_count', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    
    def faculty_count(self, obj):
        """Bu okula bağlı fakülte sayısını gösterir"""
        return obj.faculties.count()
    faculty_count.short_description = 'Fakülte Sayısı'


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """
    Fakülte modeli için admin konfigürasyonu
    """
    list_display = ('name', 'school', 'department_count', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('name', 'school__name')
    ordering = ('school__name', 'name')
    
    def department_count(self, obj):
        """Bu fakülteye bağlı bölüm sayısını gösterir"""
        return obj.departments.count()
    department_count.short_description = 'Bölüm Sayısı'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Bölüm modeli için admin konfigürasyonu
    """
    list_display = ('name', 'faculty', 'school_name', 'assistant_count', 'course_count')
    list_filter = ('faculty', 'faculty__school', 'created_at')
    search_fields = ('name', 'faculty__name', 'faculty__school__name')
    ordering = ('faculty__school__name', 'faculty__name', 'name')
    
    def school_name(self, obj):
        """Bölümün bağlı olduğu okulu gösterir"""
        return obj.faculty.school.name
    school_name.short_description = 'Okul'
    
    def assistant_count(self, obj):
        """Bu bölümdeki asistan sayısını gösterir"""
        return obj.assistants.count()
    assistant_count.short_description = 'Asistan Sayısı'
    
    def course_count(self, obj):
        """Bu bölümdeki ders sayısını gösterir"""
        return obj.courses.count()
    course_count.short_description = 'Ders Sayısı'


@admin.register(AssistantProfile)
class AssistantProfileAdmin(admin.ModelAdmin):
    """
    Asistan profili için admin konfigürasyonu
    """
    list_display = ('get_full_name', 'department', 'exam_load_score', 'phone_number')
    list_filter = ('department', 'exam_load_score')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone_number')
    ordering = ('-exam_load_score', 'user__first_name')
    
    # Raw ID widget kullanarak performansı artır
    raw_id_fields = ('user',)
    
    def get_full_name(self, obj):
        """Asistanın tam adını gösterir"""
        return obj.user.full_name
    get_full_name.short_description = 'Ad Soyad'
    
    # Admin eylemları
    actions = ['update_exam_scores']
    
    def update_exam_scores(self, request, queryset):
        """Seçili asistanların sınav puanlarını günceller"""
        updated_count = 0
        for profile in queryset:
            profile.update_exam_load_score()
            updated_count += 1
        self.message_user(request, f'{updated_count} asistanın puanı güncellendi.')
    update_exam_scores.short_description = "Sınav puanlarını güncelle"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Ders modeli için admin konfigürasyonu
    """
    list_display = ('course_code', 'course_name', 'department', 'credit', 'exam_count')
    list_filter = ('department', 'credit', 'created_at')
    search_fields = ('course_code', 'course_name', 'department__name')
    ordering = ('department__name', 'course_code')
    
    def exam_count(self, obj):
        """Bu derse ait sınav sayısını gösterir"""
        return obj.exams.count()
    exam_count.short_description = 'Sınav Sayısı'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """
    Sınav modeli için admin konfigürasyonu
    """
    list_display = (
        'course', 'exam_type', 'exam_level', 'exam_datetime', 
        'location', 'proctor_coverage', 'creator'
    )
    list_filter = (
        'exam_type', 'exam_level', 'exam_datetime', 
        'course__department', 'creator'
    )
    search_fields = (
        'course__course_code', 'course__course_name', 
        'location', 'creator__first_name', 'creator__last_name'
    )
    ordering = ('-exam_datetime',)
    
    # Tarih filtresi
    date_hierarchy = 'exam_datetime'
    
    # Raw ID widget
    raw_id_fields = ('course', 'creator')
    
    # Okunabilir alanlar (salt okunur)
    readonly_fields = ('created_at', 'updated_at')
    
    def proctor_coverage(self, obj):
        """Gözetmen ihtiyacının karşılanma durumunu görsel olarak gösterir"""
        assigned = obj.assigned_proctors_count
        needed = obj.proctor_needed_count
        percentage = (assigned / needed * 100) if needed > 0 else 0
        
        if percentage >= 100:
            color = 'green'
            status = 'Tamamlandı'
        elif percentage >= 50:
            color = 'orange'
            status = 'Kısmi'
        else:
            color = 'red'
            status = 'Eksik'
        
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color, assigned, needed, int(percentage)
        )
    proctor_coverage.short_description = 'Gözetmen Durumu'
    
    # Admin eylemları
    actions = ['clone_exams']
    
    def clone_exams(self, request, queryset):
        """Seçili sınavları klonlar"""
        cloned_count = 0
        for exam in queryset:
            exam.pk = None
            exam.exam_datetime = exam.exam_datetime.replace(year=exam.exam_datetime.year + 1)
            exam.save()
            cloned_count += 1
        self.message_user(request, f'{cloned_count} sınav bir sonraki yıl için klonlandı.')
    clone_exams.short_description = "Sınavları gelecek yıl için klonla"


@admin.register(ProctorAssignment)
class ProctorAssignmentAdmin(admin.ModelAdmin):
    """
    Gözetmen ataması için admin konfigürasyonu
    """
    list_display = (
        'get_assistant_name', 'get_exam_info', 'status', 
        'assigned_at', 'response_at', 'assigned_by'
    )
    list_filter = (
        'status', 'assigned_at', 'response_at', 
        'exam__exam_type', 'exam__exam_level'
    )
    search_fields = (
        'assistant__first_name', 'assistant__last_name', 
        'exam__course__course_code', 'exam__course__course_name'
    )
    ordering = ('-assigned_at',)
    
    # Raw ID widgets
    raw_id_fields = ('assistant', 'exam', 'assigned_by')
    
    # Okunabilir alanlar
    readonly_fields = ('assigned_at', 'response_at')
    
    def get_assistant_name(self, obj):
        """Asistan adını gösterir"""
        return obj.assistant.full_name
    get_assistant_name.short_description = 'Asistan'
    
    def get_exam_info(self, obj):
        """Sınav bilgilerini özetler"""
        return f"{obj.exam.course.course_code} - {obj.exam.get_exam_type_display()}"
    get_exam_info.short_description = 'Sınav'
    
    # Admin eylemları
    actions = ['approve_assignments', 'reject_assignments']
    
    def approve_assignments(self, request, queryset):
        """Seçili atamaları onaylar"""
        updated = 0
        for assignment in queryset.filter(status='PENDING'):
            assignment.accept_assignment()
            updated += 1
        self.message_user(request, f'{updated} atama onaylandı.')
    approve_assignments.short_description = "Seçili atamaları onayla"
    
    def reject_assignments(self, request, queryset):
        """Seçili atamaları reddeder"""
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{updated} atama reddedildi.')
    reject_assignments.short_description = "Seçili atamaları reddet"


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Takvim etkinliği için admin konfigürasyonu
    """
    list_display = (
        'title', 'get_assistant_name', 'event_type', 
        'start_datetime', 'end_datetime', 'location'
    )
    list_filter = (
        'event_type', 'start_datetime', 'is_recurring',
        'assistant__assistantprofile__department'
    )
    search_fields = (
        'title', 'description', 'assistant__first_name', 
        'assistant__last_name', 'location'
    )
    ordering = ('-start_datetime',)
    
    # Tarih filtresi
    date_hierarchy = 'start_datetime'
    
    # Raw ID widget
    raw_id_fields = ('assistant',)
    
    def get_assistant_name(self, obj):
        """Asistan adını gösterir"""
        return obj.assistant.full_name
    get_assistant_name.short_description = 'Asistan'


# Admin site özelleştirmeleri
admin.site.site_header = "Asistan Sınav Planlayıcı - Yönetim Paneli"
admin.site.site_title = "Exam Planner Admin"
admin.site.index_title = "Yönetim Paneli"
