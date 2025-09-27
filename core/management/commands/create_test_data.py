"""
Django management komutu - Test verileri oluşturur
Kullanım: python manage.py create_test_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import (
    User, School, Faculty, Department, AssistantProfile,
    Course, Exam, ProctorAssignment, CalendarEvent
)


class Command(BaseCommand):
    help = 'Test verileri oluşturur'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Test verileri oluşturuluyor...'))

        # 1. Okul yapısı oluştur
        school = School.objects.get_or_create(
            name="Teknik Üniversite",
            defaults={}
        )[0]

        faculty_eng = Faculty.objects.get_or_create(
            name="Mühendislik Fakültesi",
            school=school,
            defaults={}
        )[0]

        faculty_sci = Faculty.objects.get_or_create(
            name="Fen Edebiyat Fakültesi", 
            school=school,
            defaults={}
        )[0]

        # Bölümler
        dept_cs = Department.objects.get_or_create(
            name="Bilgisayar Mühendisliği",
            faculty=faculty_eng,
            defaults={}
        )[0]

        dept_ee = Department.objects.get_or_create(
            name="Elektrik Elektronik Mühendisliği",
            faculty=faculty_eng,
            defaults={}
        )[0]

        dept_math = Department.objects.get_or_create(
            name="Matematik Bölümü",
            faculty=faculty_sci,
            defaults={}
        )[0]

        self.stdout.write(self.style.SUCCESS('✓ Okul yapısı oluşturuldu'))

        # 2. Kullanıcılar oluştur
        # Sekreter
        secretary = User.objects.get_or_create(
            email="sekreter@university.edu.tr",
            defaults={
                'username': 'sekreter',
                'first_name': 'Sekreter',
                'last_name': 'Hanım',
                'role': 'FACULTY_SECRETARY',
                'is_active': True
            }
        )[0]
        if not secretary.has_usable_password():
            secretary.set_password('test123456')
            secretary.save()

        # Asistan 1
        assistant1 = User.objects.get_or_create(
            email="asistan1@university.edu.tr",
            defaults={
                'username': 'asistan1',
                'first_name': 'Ali',
                'last_name': 'Yılmaz',
                'role': 'ASSISTANT',
                'is_active': True
            }
        )[0]
        if not assistant1.has_usable_password():
            assistant1.set_password('test123456')
            assistant1.save()

        # Asistan 2  
        assistant2 = User.objects.get_or_create(
            email="asistan2@university.edu.tr",
            defaults={
                'username': 'asistan2',
                'first_name': 'Ayşe',
                'last_name': 'Demir',
                'role': 'ASSISTANT',
                'is_active': True
            }
        )[0]
        if not assistant2.has_usable_password():
            assistant2.set_password('test123456')
            assistant2.save()

        # Asistan 3
        assistant3 = User.objects.get_or_create(
            email="asistan3@university.edu.tr",
            defaults={
                'username': 'asistan3',
                'first_name': 'Mehmet',
                'last_name': 'Kaya',
                'role': 'ASSISTANT',
                'is_active': True
            }
        )[0]
        if not assistant3.has_usable_password():
            assistant3.set_password('test123456')
            assistant3.save()

        self.stdout.write(self.style.SUCCESS('✓ Kullanıcılar oluşturuldu'))

        # 3. Asistan profilleri oluştur
        AssistantProfile.objects.get_or_create(
            user=assistant1,
            defaults={
                'department': dept_cs,
                'exam_load_score': 5,
                'phone_number': '0555 123 45 67'
            }
        )

        AssistantProfile.objects.get_or_create(
            user=assistant2,
            defaults={
                'department': dept_ee,
                'exam_load_score': 3,
                'phone_number': '0555 234 56 78'
            }
        )

        AssistantProfile.objects.get_or_create(
            user=assistant3,
            defaults={
                'department': dept_math,
                'exam_load_score': 7,
                'phone_number': '0555 345 67 89'
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ Asistan profilleri oluşturuldu'))

        # 4. Dersler oluştur
        courses_data = [
            ('CSE101', 'Programlama Temelleri', dept_cs, 4),
            ('CSE201', 'Veri Yapıları', dept_cs, 3),
            ('CSE301', 'Veritabanı Yönetimi', dept_cs, 3),
            ('EEE101', 'Elektrik Devre Analizi', dept_ee, 4),
            ('EEE201', 'Elektronik Devreler', dept_ee, 3),
            ('MATH101', 'Calculus I', dept_math, 4),
            ('MATH201', 'Calculus II', dept_math, 4),
        ]

        courses = []
        for code, name, department, credit in courses_data:
            course = Course.objects.get_or_create(
                course_code=code,
                defaults={
                    'course_name': name,
                    'department': department,
                    'credit': credit
                }
            )[0]
            courses.append(course)

        self.stdout.write(self.style.SUCCESS('✓ Dersler oluşturuldu'))

        # 5. Sınavlar oluştur
        now = timezone.now()
        exams_data = [
            (courses[0], 'MIDTERM', 'UNDERGRADUATE', 'Amfi-1', now + timedelta(days=3), 120, 2, 85),
            (courses[1], 'FINAL', 'UNDERGRADUATE', 'Lab-205', now + timedelta(days=7), 180, 2, 60),
            (courses[2], 'MIDTERM', 'UNDERGRADUATE', 'Amfi-2', now + timedelta(days=5), 90, 1, 45),
            (courses[3], 'FINAL', 'UNDERGRADUATE', 'Lab-101', now + timedelta(days=10), 150, 3, 120),
            (courses[4], 'MIDTERM', 'GRADUATE', 'Lab-301', now + timedelta(days=14), 120, 2, 25),
            (courses[5], 'FINAL', 'UNDERGRADUATE', 'Amfi-3', now + timedelta(days=12), 180, 2, 95),
        ]

        exams = []
        for course, exam_type, level, location, exam_time, duration, proctors, students in exams_data:
            exam = Exam.objects.get_or_create(
                course=course,
                exam_type=exam_type,
                exam_datetime=exam_time,
                defaults={
                    'exam_level': level,
                    'location': location,
                    'duration_minutes': duration,
                    'proctor_needed_count': proctors,
                    'student_count': students,
                    'creator': secretary,
                    'special_notes': f'{course.course_code} dersi {exam_type.lower()} sınavı'
                }
            )[0]
            exams.append(exam)

        self.stdout.write(self.style.SUCCESS('✓ Sınavlar oluşturuldu'))

        # 6. Gözetmen atamaları oluştur
        assignments_data = [
            (assistant1, exams[0], 'ACCEPTED'),
            (assistant2, exams[0], 'ACCEPTED'), 
            (assistant1, exams[1], 'PENDING'),
            (assistant3, exams[1], 'PENDING'),
            (assistant2, exams[2], 'REJECTED', 'O tarihte başka bir işim var'),
            (assistant3, exams[3], 'ACCEPTED'),
            (assistant1, exams[4], 'PENDING'),
            (assistant2, exams[5], 'ACCEPTED'),
        ]

        for data in assignments_data:
            assistant, exam, status = data[:3]
            reason = data[3] if len(data) > 3 else None
            
            assignment, created = ProctorAssignment.objects.get_or_create(
                assistant=assistant,
                exam=exam,
                defaults={
                    'status': status,
                    'assigned_by': secretary,
                    'reason_for_rejection': reason,
                    'response_at': now if status != 'PENDING' else None
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Gözetmen atamaları oluşturuldu'))

        # 7. Asistan puanlarını güncelle
        for assistant in [assistant1, assistant2, assistant3]:
            try:
                profile = assistant.assistantprofile
                profile.update_exam_load_score()
                self.stdout.write(
                    f'✓ {assistant.full_name} puanı güncellendi: {profile.exam_load_score}'
                )
            except:
                pass

        # 8. Takvim etkinlikleri oluştur
        events_data = [
            (assistant1, 'CSE101 Dersi', now + timedelta(days=1, hours=10), 
             now + timedelta(days=1, hours=12), 'LECTURE', 'B-201'),
            (assistant1, 'Lab Çalışması', now + timedelta(days=2, hours=14),
             now + timedelta(days=2, hours=16), 'LAB', 'Lab-105'),
            (assistant2, 'Ofis Saatleri', now + timedelta(days=3, hours=13),
             now + timedelta(days=3, hours=15), 'OFFICE_HOURS', 'Oda-315'),
            (assistant3, 'Toplantı', now + timedelta(days=4, hours=9),
             now + timedelta(days=4, hours=10), 'MEETING', 'Toplantı Salonu'),
        ]

        for assistant, title, start, end, event_type, location in events_data:
            CalendarEvent.objects.get_or_create(
                assistant=assistant,
                title=title,
                start_datetime=start,
                defaults={
                    'end_datetime': end,
                    'event_type': event_type,
                    'location': location,
                    'description': f'{title} - {assistant.full_name}'
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Takvim etkinlikleri oluşturuldu'))

        # Özet bilgi
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('TEST VERİLERİ BAŞARIYLA OLUŞTURULDU!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Okullar: {School.objects.count()}')
        self.stdout.write(f'Fakülteler: {Faculty.objects.count()}')  
        self.stdout.write(f'Bölümler: {Department.objects.count()}')
        self.stdout.write(f'Kullanıcılar: {User.objects.count()}')
        self.stdout.write(f'Asistan Profilleri: {AssistantProfile.objects.count()}')
        self.stdout.write(f'Dersler: {Course.objects.count()}')
        self.stdout.write(f'Sınavlar: {Exam.objects.count()}')
        self.stdout.write(f'Gözetmen Atamaları: {ProctorAssignment.objects.count()}')
        self.stdout.write(f'Takvim Etkinlikleri: {CalendarEvent.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\nTest Kullanıcıları:'))
        self.stdout.write('Admin: admin@examplanner.com')
        self.stdout.write('Sekreter: sekreter@university.edu.tr')
        self.stdout.write('Asistan 1: asistan1@university.edu.tr')
        self.stdout.write('Asistan 2: asistan2@university.edu.tr')
        self.stdout.write('Asistan 3: asistan3@university.edu.tr')
        self.stdout.write('Tüm şifreler: test123456')
        self.stdout.write(self.style.SUCCESS('='*50))
