# Asistan Sınav Planlayıcı - Veritabanı Modelleri
# Bu dosya projenin tüm veritabanı tablolarını Python sınıfları olarak tanımlar.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Django'nun kendi User modelini genişletiyoruz
class User(AbstractUser):
    """
    Özel kullanıcı modeli - Django'nun standart User modelini genişletir.
    Email'i ana kimlik bilgisi olarak kullanır ve rol tabanlı yetkilendirme sağlar.
    """
    # Email'i ana kimlik bilgisi yapıyoruz (username yerine)
    email = models.EmailField(unique=True, verbose_name="E-posta")
    first_name = models.CharField(max_length=100, verbose_name="Ad")
    last_name = models.CharField(max_length=100, verbose_name="Soyad")
    
    ROLE_CHOICES = [
        ('ADMIN', 'Sistem Yöneticisi'),
        ('SECRETARY_RECTORATE', 'Rektörlük Sekreteri'),
        ('SECRETARY_FACULTY', 'Fakülte Sekreteri'),
        ('SECRETARY_DEPARTMENT', 'Bölüm Sekreteri'),
        ('ASSISTANT', 'Asistan'),
    ]
    role = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        verbose_name="Rol"
    )
    
    # Sekreterler ve asistanlar için bölüm/fakülte bağlantısı
    # Bu alanlar null olabilir çünkü ADMIN ve RECTORATE_SECRETARY için gerekmez
    faculty = models.ForeignKey(
        'Faculty', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Fakülte",
        help_text="Kullanıcının bağlı olduğu fakülte (sekreterler ve asistanlar için)"
    )
    
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Bölüm",
        help_text="Kullanıcının bağlı olduğu bölüm (bölüm sekreterleri ve asistanlar için)"
    )
    
    # is_active alanı kullanıcının admin onayını temsil eder
    # is_staff alanı admin paneline erişim için kullanılır
    
    USERNAME_FIELD = 'email'  # Giriş için email kullan
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        """Kullanıcının tam adını döndürür"""
        return f"{self.first_name} {self.last_name}"

    def has_secretary_permissions(self):
        """Kullanıcının sekreter yetkisine sahip olup olmadığını kontrol eder"""
        return self.role in ['SECRETARY_RECTORATE', 'SECRETARY_FACULTY', 'SECRETARY_DEPARTMENT']

    def is_assistant(self):
        """Kullanıcının asistan olup olmadığını kontrol eder"""
        return self.role == 'ASSISTANT'
    
    def get_permission_scope(self):
        """
        Kullanıcının yetki kapsamını döndürür
        """
        if self.role == 'ADMIN' or self.role == 'SECRETARY_RECTORATE':
            return 'ALL'  # Tüm okul
        elif self.role == 'SECRETARY_FACULTY' and self.faculty:
            return f'FACULTY_{self.faculty.id}'  # Sadece bir fakülte
        elif self.role == 'SECRETARY_DEPARTMENT' and self.department:
            return f'DEPARTMENT_{self.department.id}'  # Sadece bir bölüm
        elif self.role == 'ASSISTANT':
            return 'SELF'  # Sadece kendi görevleri
        return 'NONE'

    def clean(self):
        """
        Model validation - rol ve bölüm/fakülte tutarlılık kontrolü
        """
        super().clean()
        
        if self.role == 'SECRETARY_DEPARTMENT' and not self.department:
            raise ValidationError("Bölüm sekreteri için bölüm seçimi zorunludur.")
            
        if self.role == 'SECRETARY_FACULTY' and not self.faculty:
            raise ValidationError("Fakülte sekreteri için fakülte seçimi zorunludur.")
            
        if self.role == 'ASSISTANT' and not self.department:
            raise ValidationError("Asistan için bölüm seçimi zorunludur.")
            
        # Bölüm seçiliyse fakülte otomatik atanmalı
        if self.department and not self.faculty:
            self.faculty = self.department.faculty


# Hiyerarşik Yapı Modelleri
class School(models.Model):
    """
    Üniversite/Okul modeli - En üst seviye organizasyon birimi
    """
    name = models.CharField(max_length=255, verbose_name="Okul Adı")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Okul"
        verbose_name_plural = "Okullar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Faculty(models.Model):
    """
    Fakülte modeli - Okulun alt birimi
    """
    name = models.CharField(max_length=255, verbose_name="Fakülte Adı")
    school = models.ForeignKey(
        School, 
        on_delete=models.CASCADE, 
        verbose_name="Okul",
        related_name="faculties"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fakülte"
        verbose_name_plural = "Fakülteler"
        ordering = ['school__name', 'name']

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Department(models.Model):
    """
    Bölüm modeli - Fakültenin alt birimi
    """
    name = models.CharField(max_length=255, verbose_name="Bölüm Adı")
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.CASCADE, 
        verbose_name="Fakülte",
        related_name="departments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bölüm"
        verbose_name_plural = "Bölümler"
        ordering = ['faculty__name', 'name']

    def __str__(self):
        return f"{self.faculty.name} - {self.name}"


class AssistantProfile(models.Model):
    """
    Asistanlara özel profil bilgileri - User modeliyle birebir ilişki
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True,
        verbose_name="Kullanıcı"
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="Bölüm",
        related_name="assistants"
    )
    exam_load_score = models.IntegerField(
        default=0, 
        verbose_name="Sınav Yükü Puanı",
        help_text="Asistanın aldığı görevlerin toplam puanı"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Telefon Numarası"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asistan Profili"
        verbose_name_plural = "Asistan Profilleri"

    def __str__(self):
        return f"{self.user.full_name} - Puan: {self.exam_load_score}"

    def update_exam_load_score(self):
        """
        Asistanın sınav yükü puanını güncel görevlere göre hesaplar
        """
        from django.db.models import Sum
        # Kabul edilen sınavların puanlarını topla
        accepted_assignments = self.user.proctorassignment_set.filter(
            status='ACCEPTED'
        )
        
        total_score = 0
        for assignment in accepted_assignments:
            # Her sınav türü için farklı puanlar
            if assignment.exam.exam_level == 'UNDERGRADUATE':
                total_score += 1
            elif assignment.exam.exam_level == 'GRADUATE':
                total_score += 2
            elif assignment.exam.exam_level == 'DOCTORAL':
                total_score += 3
                
        self.exam_load_score = total_score
        self.save()
        
        logger.info(f"Asistan {self.user.full_name} puanı güncellendi: {total_score}")
        return total_score


# Ders ve Sınav Modelleri
class Course(models.Model):
    """
    Ders modeli - Sınavların bağlı olduğu dersler
    """
    course_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Ders Kodu",
        help_text="Örnek: CSE101, MATH201"
    )
    course_name = models.CharField(
        max_length=255, 
        verbose_name="Ders Adı"
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE,
        verbose_name="Bölüm",
        related_name="courses"
    )
    credit = models.PositiveIntegerField(
        default=3, 
        verbose_name="Kredi",
        help_text="Dersin kredi değeri"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ders"
        verbose_name_plural = "Dersler"
        ordering = ['department__name', 'course_code']

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Exam(models.Model):
    """
    Sınav modeli - Ana sınav bilgilerini tutar
    """
    EXAM_TYPE_CHOICES = [
        ('MIDTERM', 'Ara Sınav'),
        ('FINAL', 'Final Sınavı'),
        ('MAKEUP', 'Bütünleme Sınavı'),
        ('RESIT', 'Tekrar Sınavı'),
    ]
    
    EXAM_LEVEL_CHOICES = [
        ('UNDERGRADUATE', 'Lisans'),
        ('GRADUATE', 'Yüksek Lisans'),
        ('DOCTORAL', 'Doktora'),
    ]

    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        verbose_name="Ders",
        related_name="exams"
    )
    exam_type = models.CharField(
        max_length=50, 
        choices=EXAM_TYPE_CHOICES,
        verbose_name="Sınav Türü"
    )
    exam_level = models.CharField(
        max_length=50, 
        choices=EXAM_LEVEL_CHOICES,
        verbose_name="Sınav Seviyesi"
    )
    location = models.CharField(
        max_length=255, 
        verbose_name="Sınav Yeri",
        help_text="Örnek: Amfi-1, Lab-205"
    )
    exam_datetime = models.DateTimeField(verbose_name="Sınav Tarihi ve Saati")
    duration_minutes = models.PositiveIntegerField(
        default=120, 
        verbose_name="Sınav Süresi (Dakika)"
    )
    proctor_needed_count = models.PositiveIntegerField(
        verbose_name="Gerekli Gözetmen Sayısı",
        help_text="Bu sınav için kaç gözetmen gerekli"
    )
    student_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Öğrenci Sayısı",
        help_text="Sınava katılacak öğrenci sayısı"
    )
    special_notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Özel Notlar",
        help_text="Sınav hakkında özel notlar veya talimatlar"
    )
    creator = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Oluşturan",
        related_name="created_exams"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sınav"
        verbose_name_plural = "Sınavlar"
        ordering = ['-exam_datetime']

    def __str__(self):
        return f"{self.course.course_code} - {self.get_exam_type_display()} ({self.exam_datetime.strftime('%d.%m.%Y %H:%M')})"

    def clean(self):
        """Model doğrulama kuralları"""
        # Sınav tarihi geçmişte olamaz
        if self.exam_datetime and self.exam_datetime < timezone.now():
            raise ValidationError("Sınav tarihi geçmişte olamaz.")
        
        # Gözetmen sayısı 0'dan büyük olmalı
        if self.proctor_needed_count <= 0:
            raise ValidationError("Gözetmen sayısı 0'dan büyük olmalıdır.")

    @property
    def exam_end_time(self):
        """Sınavın bitiş zamanını hesaplar"""
        from datetime import timedelta
        return self.exam_datetime + timedelta(minutes=self.duration_minutes)

    @property
    def assigned_proctors_count(self):
        """Atanan gözetmen sayısını döndürür"""
        return self.proctorassignment_set.filter(status='ACCEPTED').count()

    @property
    def pending_assignments_count(self):
        """Bekleyen atama sayısını döndürür"""
        return self.proctorassignment_set.filter(status='PENDING').count()

    @property
    def is_fully_assigned(self):
        """Sınavın tüm gözetmen ihtiyacının karşılanıp karşılanmadığını kontrol eder"""
        return self.assigned_proctors_count >= self.proctor_needed_count


# Asistanların Sınavlara Atanma Durumunu Tutan Ara Tablo
class ProctorAssignment(models.Model):
    """
    Gözetmen atama modeli - Asistanların sınavlara atanma durumunu yönetir
    """
    STATUS_CHOICES = [
        ('PENDING', 'Beklemede'),
        ('ACCEPTED', 'Kabul Edildi'),
        ('REJECTED', 'Reddedildi'),
        ('EXCUSED', 'Mazeretli'),
    ]
    
    assistant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Asistan",
        limit_choices_to={'role': 'ASSISTANT'}
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE,
        verbose_name="Sınav"
    )
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name="Durum"
    )
    reason_for_rejection = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Red/Mazeret Nedeni",
        help_text="Görev reddedilirse veya mazeret bildirilirse açıklama"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Atama Tarihi"
    )
    response_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Yanıt Tarihi",
        help_text="Asistanın yanıt verdiği tarih"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="made_assignments",
        verbose_name="Atamayı Yapan",
        limit_choices_to={'role__in': ['RECTORATE_SECRETARY', 'FACULTY_SECRETARY', 'DEPARTMENT_SECRETARY']}
    )

    class Meta:
        unique_together = ('assistant', 'exam')  # Bir asistan bir sınava sadece bir kez atanabilir
        verbose_name = "Gözetmen Ataması"
        verbose_name_plural = "Gözetmen Atamaları"
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.assistant.full_name} - {self.exam} ({self.get_status_display()})"

    def clean(self):
        """Model doğrulama kuralları"""
        # Asistan rolü kontrolü
        if self.assistant.role != 'ASSISTANT':
            raise ValidationError("Sadece asistan rolündeki kullanıcılar gözetmen olarak atanabilir.")
        
        # Aynı zamanda başka sınav çakışması kontrolü
        if self.assistant and self.exam:
            conflicting_assignments = ProctorAssignment.objects.filter(
                assistant=self.assistant,
                status='ACCEPTED',
                exam__exam_datetime__range=[
                    self.exam.exam_datetime,
                    self.exam.exam_end_time
                ]
            ).exclude(id=self.id)
            
            if conflicting_assignments.exists():
                raise ValidationError("Bu asistan aynı zamanda başka bir sınavda görev almaktadır.")

    def accept_assignment(self, reason=None):
        """Görev atamasını kabul eder"""
        self.status = 'ACCEPTED'
        self.response_at = timezone.now()
        if reason:
            self.reason_for_rejection = reason
        self.save()
        
        # Asistanın puanını güncelle
        try:
            profile = self.assistant.assistantprofile
            profile.update_exam_load_score()
        except AssistantProfile.DoesNotExist:
            pass
        
        logger.info(f"Görev ataması kabul edildi: {self}")

    def reject_assignment(self, reason):
        """Görev atamasını reddeder"""
        self.status = 'REJECTED'
        self.reason_for_rejection = reason
        self.response_at = timezone.now()
        self.save()
        
        logger.info(f"Görev ataması reddedildi: {self} - Sebep: {reason}")

    def mark_excused(self, reason):
        """Mazeret bildirir"""
        self.status = 'EXCUSED'
        self.reason_for_rejection = reason
        self.response_at = timezone.now()
        self.save()
        
        logger.info(f"Mazeret bildirildi: {self} - Sebep: {reason}")


# Asistanların Kişisel Takvim Etkinlikleri
class CalendarEvent(models.Model):
    """
    Takvim etkinlikleri modeli - Asistanların kişisel programlarını yönetir
    """
    EVENT_TYPE_CHOICES = [
        ('LECTURE', 'Ders'),
        ('LAB', 'Laboratuvar'),
        ('MEETING', 'Toplantı'),
        ('OFFICE_HOURS', 'Ofis Saatleri'),
        ('PERSONAL', 'Kişisel'),
        ('EXAM_DUTY', 'Sınav Görevi'),
    ]
    
    assistant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Asistan",
        limit_choices_to={'role': 'ASSISTANT'},
        related_name="calendar_events"
    )
    title = models.CharField(
        max_length=255, 
        verbose_name="Başlık"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Açıklama"
    )
    start_datetime = models.DateTimeField(verbose_name="Başlangıç Tarihi ve Saati")
    end_datetime = models.DateTimeField(verbose_name="Bitiş Tarihi ve Saati")
    event_type = models.CharField(
        max_length=50, 
        choices=EVENT_TYPE_CHOICES,
        verbose_name="Etkinlik Türü"
    )
    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Yer"
    )
    is_recurring = models.BooleanField(
        default=False,
        verbose_name="Tekrar Eden Etkinlik"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Takvim Etkinliği"
        verbose_name_plural = "Takvim Etkinlikleri"
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.assistant.full_name} - {self.title} ({self.start_datetime.strftime('%d.%m.%Y %H:%M')})"

    def clean(self):
        """Model doğrulama kuralları"""
        # Bitiş zamanı başlangıç zamanından sonra olmalı
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("Bitiş zamanı başlangıç zamanından sonra olmalıdır.")
        
        # Asistan rolü kontrolü
        if self.assistant.role != 'ASSISTANT':
            raise ValidationError("Takvim etkinlikleri sadece asistanlar için oluşturulabilir.")

    @property
    def duration_hours(self):
        """Etkinliğin süresini saat cinsinden döndürür"""
        delta = self.end_datetime - self.start_datetime
        return delta.total_seconds() / 3600

    def has_conflict_with_exam(self, exam):
        """Verilen sınav ile çakışma olup olmadığını kontrol eder"""
        exam_start = exam.exam_datetime
        exam_end = exam.exam_end_time
        
        return not (self.end_datetime <= exam_start or self.start_datetime >= exam_end)
