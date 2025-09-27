# Django Forms - Kullanıcı arayüzü formları
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, Exam, Course, ProctorAssignment, CalendarEvent, Department


class CustomUserCreationForm(UserCreationForm):
    """
    Özel kullanıcı kayıt formu
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@university.edu.tr'
        })
    )
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adınız'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Soyadınız'
        })
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'kullanici_adi'
            })
        }

    def clean_email(self):
        """E-posta doğrulama"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email

    def save(self, commit=True):
        """Kullanıcı kaydetme"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user


class ExamCreationForm(forms.ModelForm):
    """
    Sınav oluşturma formu
    """
    class Meta:
        model = Exam
        fields = [
            'course', 'exam_type', 'exam_level', 'location', 
            'exam_datetime', 'duration_minutes', 'proctor_needed_count', 
            'student_count', 'special_notes'
        ]
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'exam_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'exam_level': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örnek: Amfi-1, Lab-205',
                'required': True
            }),
            'exam_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '30',
                'max': '300',
                'step': '15',
                'value': '120'
            }),
            'proctor_needed_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'value': '2'
            }),
            'student_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '50'
            }),
            'special_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Sınav hakkında özel notlar veya talimatlar...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Course dropdown'u için queryset optimize et
        self.fields['course'].queryset = Course.objects.select_related('department').all()

    def clean_exam_datetime(self):
        """Sınav tarihi doğrulama"""
        exam_datetime = self.cleaned_data.get('exam_datetime')
        
        if exam_datetime and exam_datetime <= timezone.now():
            raise ValidationError("Sınav tarihi gelecekte olmalıdır.")
        
        return exam_datetime

    def clean_proctor_needed_count(self):
        """Gözetmen sayısı doğrulama"""
        count = self.cleaned_data.get('proctor_needed_count')
        student_count = self.cleaned_data.get('student_count', 0)
        
        if count and student_count:
            # Her 25 öğrenci için 1 gözetmen kuralı
            recommended_count = max(1, (student_count + 24) // 25)
            if count < recommended_count:
                raise ValidationError(
                    f"Öğrenci sayısına göre en az {recommended_count} gözetmen önerilir."
                )
        
        return count


class AssignmentForm(forms.ModelForm):
    """
    Gözetmen atama formu
    """
    class Meta:
        model = ProctorAssignment
        fields = ['assistant', 'exam']
        widgets = {
            'assistant': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'exam': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sadece aktif asistanları göster
        self.fields['assistant'].queryset = User.objects.filter(
            role='ASSISTANT',
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Sadece gelecekteki sınavları göster
        self.fields['exam'].queryset = Exam.objects.filter(
            exam_datetime__gte=timezone.now()
        ).select_related('course').order_by('exam_datetime')

    def clean(self):
        """Form geneli doğrulama"""
        cleaned_data = super().clean()
        assistant = cleaned_data.get('assistant')
        exam = cleaned_data.get('exam')

        if assistant and exam:
            # Çakışma kontrolü
            conflicting_assignments = ProctorAssignment.objects.filter(
                assistant=assistant,
                status='ACCEPTED',
                exam__exam_datetime__range=[
                    exam.exam_datetime,
                    exam.exam_end_time
                ]
            )
            
            if self.instance.pk:
                conflicting_assignments = conflicting_assignments.exclude(pk=self.instance.pk)
            
            if conflicting_assignments.exists():
                raise ValidationError(
                    "Bu asistan aynı zamanda başka bir sınava atanmıştır."
                )
            
            # Mevcut atama kontrolü
            existing = ProctorAssignment.objects.filter(
                assistant=assistant,
                exam=exam
            )
            
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    "Bu asistan zaten bu sınava atanmıştır."
                )

        return cleaned_data


class CalendarEventForm(forms.ModelForm):
    """
    Takvim etkinliği formu
    """
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'start_datetime', 
            'end_datetime', 'event_type', 'location', 'is_recurring'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etkinlik başlığı',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Etkinlik açıklaması...'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etkinlik yeri'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean(self):
        """Form geneli doğrulama"""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')

        if start_datetime and end_datetime:
            if end_datetime <= start_datetime:
                raise ValidationError(
                    "Bitiş zamanı başlangıç zamanından sonra olmalıdır."
                )
            
            # Maksimum 12 saat süre kontrolü
            duration = end_datetime - start_datetime
            if duration.total_seconds() > 12 * 3600:
                raise ValidationError(
                    "Etkinlik süresi 12 saati geçemez."
                )

        return cleaned_data


class ExamSearchForm(forms.Form):
    """
    Sınav arama formu
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ders kodu, ders adı veya mekan ara...'
        })
    )
    
    date_filter = forms.ChoiceField(
        choices=[
            ('', 'Tüm Tarihler'),
            ('upcoming', 'Yaklaşan Sınavlar'),
            ('past', 'Geçmiş Sınavlar'),
            ('today', 'Bugün'),
            ('this_week', 'Bu Hafta'),
            ('next_week', 'Gelecek Hafta')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    exam_type = forms.ChoiceField(
        choices=[('', 'Tüm Türler')] + Exam.EXAM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    exam_level = forms.ChoiceField(
        choices=[('', 'Tüm Seviyeler')] + Exam.EXAM_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status_filter = forms.ChoiceField(
        choices=[
            ('', 'Tüm Durumlar'),
            ('complete', 'Gözetmen Ataması Tamamlanmış'),
            ('incomplete', 'Gözetmen Ataması Eksik'),
            ('no_assignment', 'Hiç Atama Yapılmamış')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class AssignmentSearchForm(forms.Form):
    """
    Gözetmen ataması arama formu
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asistan adı veya ders kodu ara...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Tüm Durumlar')] + ProctorAssignment.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Tüm Bölümler",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    exam_type = forms.ChoiceField(
        choices=[('', 'Tüm Sınav Türleri')] + Exam.EXAM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
