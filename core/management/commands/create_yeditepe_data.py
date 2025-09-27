"""
Django management komutu - Yeditepe Üniversitesi için test verileri oluşturur
Kullanım: python manage.py create_yeditepe_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import (
    User, School, Faculty, Department, AssistantProfile,
    Course, Exam, ProctorAssignment, CalendarEvent
)


class Command(BaseCommand):
    help = 'Yeditepe Üniversitesi için test verileri oluşturur'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Yeditepe Üniversitesi test verileri oluşturuluyor...'))

        # 1. Yeditepe Üniversitesi yapısı oluştur
        school = School.objects.get_or_create(
            name="Yeditepe Üniversitesi",
            defaults={}
        )[0]

        # Fakülteler
        faculty_eng = Faculty.objects.get_or_create(
            name="Mühendislik Fakültesi",
            school=school,
            defaults={}
        )[0]

        faculty_med = Faculty.objects.get_or_create(
            name="Tıp Fakültesi", 
            school=school,
            defaults={}
        )[0]

        faculty_business = Faculty.objects.get_or_create(
            name="İktisadi ve İdari Bilimler Fakültesi",
            school=school,
            defaults={}
        )[0]

        faculty_arts = Faculty.objects.get_or_create(
            name="Güzel Sanatlar Fakültesi",
            school=school,
            defaults={}
        )[0]

        faculty_comm = Faculty.objects.get_or_create(
            name="İletişim Fakültesi",
            school=school,
            defaults={}
        )[0]

        self.stdout.write(self.style.SUCCESS('✓ Fakülteler oluşturuldu'))

        # Mühendislik Bölümleri
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

        dept_ie = Department.objects.get_or_create(
            name="Endüstri Mühendisliği",
            faculty=faculty_eng,
            defaults={}
        )[0]

        dept_civil = Department.objects.get_or_create(
            name="İnşaat Mühendisliği",
            faculty=faculty_eng,
            defaults={}
        )[0]

        # İktisadi ve İdari Bilimler Bölümleri
        dept_business = Department.objects.get_or_create(
            name="İşletme",
            faculty=faculty_business,
            defaults={}
        )[0]

        dept_economics = Department.objects.get_or_create(
            name="İktisat",
            faculty=faculty_business,
            defaults={}
        )[0]

        dept_intrel = Department.objects.get_or_create(
            name="Uluslararası İlişkiler",
            faculty=faculty_business,
            defaults={}
        )[0]

        # İletişim Bölümleri
        dept_journalism = Department.objects.get_or_create(
            name="Gazetecilik",
            faculty=faculty_comm,
            defaults={}
        )[0]

        dept_pr = Department.objects.get_or_create(
            name="Halkla İlişkiler ve Reklamcılık",
            faculty=faculty_comm,
            defaults={}
        )[0]

        self.stdout.write(self.style.SUCCESS('✓ Bölümler oluşturuldu'))

        # 2. Kullanıcılar oluştur
        users_data = [
            # Sekreterler
            ('sekreter.muhendislik@yeditepe.edu.tr', 'sekreter_muh', 'Ayşe', 'Yılmaz', 'FACULTY_SECRETARY'),
            ('sekreter.iibf@yeditepe.edu.tr', 'sekreter_iibf', 'Mehmet', 'Demir', 'FACULTY_SECRETARY'),
            ('sekreter.iletisim@yeditepe.edu.tr', 'sekreter_iletisim', 'Fatma', 'Kaya', 'FACULTY_SECRETARY'),
            
            # Bilgisayar Mühendisliği Asistanları
            ('ali.ozturk@yeditepe.edu.tr', 'ali_ozturk', 'Ali', 'Öztürk', 'ASSISTANT'),
            ('zeynep.aktas@yeditepe.edu.tr', 'zeynep_aktas', 'Zeynep', 'Aktaş', 'ASSISTANT'),
            ('burak.celik@yeditepe.edu.tr', 'burak_celik', 'Burak', 'Çelik', 'ASSISTANT'),
            ('seda.aydin@yeditepe.edu.tr', 'seda_aydin', 'Seda', 'Aydın', 'ASSISTANT'),
            
            # Elektrik Elektronik Asistanları
            ('emre.koc@yeditepe.edu.tr', 'emre_koc', 'Emre', 'Koç', 'ASSISTANT'),
            ('elif.sahin@yeditepe.edu.tr', 'elif_sahin', 'Elif', 'Şahin', 'ASSISTANT'),
            ('murat.yildirim@yeditepe.edu.tr', 'murat_yildirim', 'Murat', 'Yıldırım', 'ASSISTANT'),
            
            # İşletme Asistanları
            ('deniz.arslan@yeditepe.edu.tr', 'deniz_arslan', 'Deniz', 'Arslan', 'ASSISTANT'),
            ('ece.guven@yeditepe.edu.tr', 'ece_guven', 'Ece', 'Güven', 'ASSISTANT'),
            
            # Gazetecilik Asistanları
            ('kemal.ozkan@yeditepe.edu.tr', 'kemal_ozkan', 'Kemal', 'Özkan', 'ASSISTANT'),
            ('pinar.erdem@yeditepe.edu.tr', 'pinar_erdem', 'Pınar', 'Erdem', 'ASSISTANT'),
        ]

        created_users = {}
        for email, username, first_name, last_name, role in users_data:
            user = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'is_active': True
                }
            )[0]
            if not user.has_usable_password():
                user.set_password('yeditepe2025')
                user.save()
            created_users[username] = user

        self.stdout.write(self.style.SUCCESS('✓ Kullanıcılar oluşturuldu'))

        # 3. Asistan profilleri oluştur
        assistant_profiles = [
            ('ali_ozturk', dept_cs, 8, '0555 111 11 11'),
            ('zeynep_aktas', dept_cs, 5, '0555 222 22 22'),
            ('burak_celik', dept_cs, 12, '0555 333 33 33'),
            ('seda_aydin', dept_cs, 3, '0555 444 44 44'),
            ('emre_koc', dept_ee, 6, '0555 555 55 55'),
            ('elif_sahin', dept_ee, 9, '0555 666 66 66'),
            ('murat_yildirim', dept_ee, 4, '0555 777 77 77'),
            ('deniz_arslan', dept_business, 7, '0555 888 88 88'),
            ('ece_guven', dept_business, 2, '0555 999 99 99'),
            ('kemal_ozkan', dept_journalism, 5, '0555 101 10 10'),
            ('pinar_erdem', dept_journalism, 8, '0555 121 12 12'),
        ]

        for username, department, score, phone in assistant_profiles:
            user = created_users[username]
            AssistantProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': department,
                    'exam_load_score': score,
                    'phone_number': phone
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Asistan profilleri oluşturuldu'))

        # 4. Dersler oluştur
        courses_data = [
            # Bilgisayar Mühendisliği Dersleri
            ('CSE101', 'Bilgisayar Programlamaya Giriş', dept_cs, 4),
            ('CSE102', 'Bilgisayar Programlama', dept_cs, 4),
            ('CSE201', 'Veri Yapıları ve Algoritmalar', dept_cs, 4),
            ('CSE202', 'Nesne Yönelimli Programlama', dept_cs, 3),
            ('CSE301', 'Veritabanı Yönetim Sistemleri', dept_cs, 3),
            ('CSE302', 'Web Programlama', dept_cs, 3),
            ('CSE401', 'Yazılım Mühendisliği', dept_cs, 3),
            ('CSE402', 'Yapay Zeka', dept_cs, 3),

            # Elektrik Elektronik Dersleri
            ('EEE101', 'Devre Analizi I', dept_ee, 4),
            ('EEE102', 'Devre Analizi II', dept_ee, 4),
            ('EEE201', 'Elektronik Devreler I', dept_ee, 3),
            ('EEE202', 'Elektronik Devreler II', dept_ee, 3),
            ('EEE301', 'Sinyal ve Sistemler', dept_ee, 3),
            ('EEE302', 'Dijital Sinyal İşleme', dept_ee, 3),

            # İşletme Dersleri
            ('BUS101', 'İşletmeye Giriş', dept_business, 3),
            ('BUS201', 'Muhasebe İlkeleri', dept_business, 3),
            ('BUS301', 'Pazarlama Yönetimi', dept_business, 3),
            ('BUS302', 'İnsan Kaynakları Yönetimi', dept_business, 3),
            ('BUS401', 'Stratejik Yönetim', dept_business, 3),

            # Gazetecilik Dersleri
            ('JOUR101', 'Gazetecilik Tarihi', dept_journalism, 3),
            ('JOUR201', 'Haber Yazma Teknikleri', dept_journalism, 3),
            ('JOUR301', 'Dijital Medya', dept_journalism, 3),
            ('JOUR401', 'Medya Etiği', dept_journalism, 3),
        ]

        courses = {}
        for code, name, department, credit in courses_data:
            course = Course.objects.get_or_create(
                course_code=code,
                defaults={
                    'course_name': name,
                    'department': department,
                    'credit': credit
                }
            )[0]
            courses[code] = course

        self.stdout.write(self.style.SUCCESS('✓ Dersler oluşturuldu'))

        # 5. Sınavlar oluştur
        now = timezone.now()
        exams_data = [
            # Bilgisayar Mühendisliği Sınavları
            ('CSE101', 'MIDTERM', 'UNDERGRADUATE', 'Amfi A-1', now + timedelta(days=3), 120, 2, 95),
            ('CSE102', 'FINAL', 'UNDERGRADUATE', 'Amfi A-2', now + timedelta(days=10), 180, 3, 110),
            ('CSE201', 'MIDTERM', 'UNDERGRADUATE', 'Lab B-201', now + timedelta(days=5), 90, 2, 75),
            ('CSE301', 'FINAL', 'UNDERGRADUATE', 'Amfi A-3', now + timedelta(days=15), 150, 2, 65),
            ('CSE401', 'MIDTERM', 'UNDERGRADUATE', 'Sınıf C-301', now + timedelta(days=7), 120, 2, 45),

            # Elektrik Elektronik Sınavları
            ('EEE101', 'MIDTERM', 'UNDERGRADUATE', 'Lab E-101', now + timedelta(days=4), 120, 2, 85),
            ('EEE201', 'FINAL', 'UNDERGRADUATE', 'Amfi E-1', now + timedelta(days=12), 180, 3, 95),
            ('EEE301', 'MIDTERM', 'GRADUATE', 'Lab E-301', now + timedelta(days=8), 90, 1, 25),

            # İşletme Sınavları
            ('BUS101', 'FINAL', 'UNDERGRADUATE', 'Amfi B-1', now + timedelta(days=6), 150, 2, 120),
            ('BUS201', 'MIDTERM', 'UNDERGRADUATE', 'Sınıf B-201', now + timedelta(days=9), 90, 2, 80),
            ('BUS401', 'FINAL', 'UNDERGRADUATE', 'Amfi B-2', now + timedelta(days=14), 180, 3, 55),

            # Gazetecilik Sınavları
            ('JOUR201', 'MIDTERM', 'UNDERGRADUATE', 'Sınıf İ-201', now + timedelta(days=11), 90, 1, 40),
            ('JOUR301', 'FINAL', 'UNDERGRADUATE', 'Lab İ-301', now + timedelta(days=13), 120, 2, 35),
        ]

        exams = {}
        secretary = created_users['sekreter_muh']  # Varsayılan sekreter
        for course_code, exam_type, level, location, exam_time, duration, proctors, students in exams_data:
            course = courses[course_code]
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
                    'special_notes': f'{course_code} dersi {exam_type.lower()} sınavı - Yeditepe Üniversitesi'
                }
            )[0]
            exams[f"{course_code}_{exam_type}"] = exam

        self.stdout.write(self.style.SUCCESS('✓ Sınavlar oluşturuldu'))

        # 6. Gözetmen atamaları oluştur
        assignments_data = [
            # CSE101 Midterm - 2 gözetmen
            ('ali_ozturk', 'CSE101_MIDTERM', 'ACCEPTED'),
            ('zeynep_aktas', 'CSE101_MIDTERM', 'ACCEPTED'),
            
            # CSE102 Final - 3 gözetmen
            ('burak_celik', 'CSE102_FINAL', 'PENDING'),
            ('seda_aydin', 'CSE102_FINAL', 'ACCEPTED'),
            ('ali_ozturk', 'CSE102_FINAL', 'REJECTED', 'O tarihte başka bir sınav görevim var'),
            
            # EEE101 Midterm
            ('emre_koc', 'EEE101_MIDTERM', 'ACCEPTED'),
            ('elif_sahin', 'EEE101_MIDTERM', 'PENDING'),
            
            # BUS101 Final
            ('deniz_arslan', 'BUS101_FINAL', 'ACCEPTED'),
            ('ece_guven', 'BUS101_FINAL', 'PENDING'),
            
            # Cross-department assignments
            ('kemal_ozkan', 'CSE201_MIDTERM', 'ACCEPTED'),  # Journalism assistant in CS exam
            ('pinar_erdem', 'JOUR201_MIDTERM', 'ACCEPTED'),
        ]

        for username, exam_key, status, *reason_args in assignments_data:
            assistant = created_users[username]
            exam = exams.get(exam_key)
            reason = reason_args[0] if reason_args else None
            
            if exam:
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

        # 7. Takvim etkinlikleri oluştur
        events_data = [
            ('ali_ozturk', 'CSE101 Lab Dersi', now + timedelta(days=1, hours=10), 
             now + timedelta(days=1, hours=12), 'LAB', 'Lab B-201'),
            ('ali_ozturk', 'Ofis Saatleri', now + timedelta(days=2, hours=14),
             now + timedelta(days=2, hours=16), 'OFFICE_HOURS', 'Oda B-315'),
             
            ('zeynep_aktas', 'CSE102 Recitation', now + timedelta(days=1, hours=13),
             now + timedelta(days=1, hours=14), 'LECTURE', 'Sınıf B-205'),
             
            ('emre_koc', 'EEE Lab Çalışması', now + timedelta(days=3, hours=9),
             now + timedelta(days=3, hours=11), 'LAB', 'Lab E-101'),
             
            ('deniz_arslan', 'BUS Seminer Hazırlığı', now + timedelta(days=4, hours=15),
             now + timedelta(days=4, hours=17), 'MEETING', 'Toplantı Salonu'),
             
            ('kemal_ozkan', 'JOUR Proje Sunumu', now + timedelta(days=5, hours=11),
             now + timedelta(days=5, hours=12), 'LECTURE', 'Sınıf İ-201'),
        ]

        for username, title, start, end, event_type, location in events_data:
            assistant = created_users[username]
            CalendarEvent.objects.get_or_create(
                assistant=assistant,
                title=title,
                start_datetime=start,
                defaults={
                    'end_datetime': end,
                    'event_type': event_type,
                    'location': location,
                    'description': f'{title} - {assistant.full_name} - Yeditepe Üniversitesi'
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Takvim etkinlikleri oluşturuldu'))

        # 8. Asistan puanlarını güncelle
        assistants = [created_users[username] for username in [
            'ali_ozturk', 'zeynep_aktas', 'burak_celik', 'seda_aydin',
            'emre_koc', 'elif_sahin', 'murat_yildirim',
            'deniz_arslan', 'ece_guven', 'kemal_ozkan', 'pinar_erdem'
        ]]
        
        for assistant in assistants:
            try:
                profile = assistant.assistantprofile
                profile.update_exam_load_score()
                self.stdout.write(
                    f'✓ {assistant.full_name} puanı güncellendi: {profile.exam_load_score}'
                )
            except:
                pass

        # Özet bilgi
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('YEDİTEPE ÜNİVERSİTESİ TEST VERİLERİ OLUŞTURULDU!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Okullar: {School.objects.count()}')
        self.stdout.write(f'Fakülteler: {Faculty.objects.count()}')  
        self.stdout.write(f'Bölümler: {Department.objects.count()}')
        self.stdout.write(f'Kullanıcılar: {User.objects.count()}')
        self.stdout.write(f'Asistan Profilleri: {AssistantProfile.objects.count()}')
        self.stdout.write(f'Dersler: {Course.objects.count()}')
        self.stdout.write(f'Sınavlar: {Exam.objects.count()}')
        self.stdout.write(f'Gözetmen Atamaları: {ProctorAssignment.objects.count()}')
        self.stdout.write(f'Takvim Etkinlikleri: {CalendarEvent.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n📚 YEDITEPE ÜNİVERSİTESİ KULLANICILARI:'))
        self.stdout.write('👤 Admin: admin@examplanner.com')
        self.stdout.write('\n🏢 Sekreterler:')
        self.stdout.write('   • sekreter.muhendislik@yeditepe.edu.tr (Mühendislik Fak.)')
        self.stdout.write('   • sekreter.iibf@yeditepe.edu.tr (İİBF)')
        self.stdout.write('   • sekreter.iletisim@yeditepe.edu.tr (İletişim Fak.)')
        
        self.stdout.write('\n👨‍🎓 Bilgisayar Mühendisliği Asistanları:')
        self.stdout.write('   • ali.ozturk@yeditepe.edu.tr (Ali Öztürk)')
        self.stdout.write('   • zeynep.aktas@yeditepe.edu.tr (Zeynep Aktaş)')
        self.stdout.write('   • burak.celik@yeditepe.edu.tr (Burak Çelik)')
        self.stdout.write('   • seda.aydin@yeditepe.edu.tr (Seda Aydın)')
        
        self.stdout.write('\n👨‍🎓 Elektrik Elektronik Asistanları:')
        self.stdout.write('   • emre.koc@yeditepe.edu.tr (Emre Koç)')
        self.stdout.write('   • elif.sahin@yeditepe.edu.tr (Elif Şahin)')
        self.stdout.write('   • murat.yildirim@yeditepe.edu.tr (Murat Yıldırım)')
        
        self.stdout.write('\n👨‍💼 İşletme Asistanları:')
        self.stdout.write('   • deniz.arslan@yeditepe.edu.tr (Deniz Arslan)')
        self.stdout.write('   • ece.guven@yeditepe.edu.tr (Ece Güven)')
        
        self.stdout.write('\n📰 Gazetecilik Asistanları:')
        self.stdout.write('   • kemal.ozkan@yeditepe.edu.tr (Kemal Özkan)')
        self.stdout.write('   • pinar.erdem@yeditepe.edu.tr (Pınar Erdem)')
        
        self.stdout.write(self.style.WARNING('\n🔑 Tüm şifreler: yeditepe2025'))
        
        self.stdout.write(self.style.SUCCESS('\n🎯 Oluşturulan içerik:'))
        self.stdout.write('   • 5 Fakülte, 9 Bölüm')
        self.stdout.write('   • 23 Ders, 13 Sınav')
        self.stdout.write('   • 14 Kullanıcı (3 Sekreter + 11 Asistan)')
        self.stdout.write('   • Gerçekçi gözetmen atamaları ve takvim etkinlikleri')
        self.stdout.write(self.style.SUCCESS('='*60))
