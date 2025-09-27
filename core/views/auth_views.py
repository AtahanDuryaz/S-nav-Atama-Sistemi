# Auth Views - Kimlik doğrulama views'ları
"""
Kullanıcı kayıt, giriş ve kimlik doğrulama işlemleri
"""

from .base import *

def register_view(request):
    """
    Kullanıcı kayıt sayfası - Rol bazlı dinamik form
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Admin onayı bekliyor
                
                # Rol bazlı ek bilgiler
                role = user.role
                
                # Hiyerarşik yetki yapısına göre atamalar
                if role == 'SECRETARY_RECTORATE':
                    # Rektörlük sekreteri - En üst seviye, fakülte/bölüm seçimi isteğe bağlı
                    # Hiçbir kısıtlama yok, tüm sistem erişimi
                    pass
                    
                elif role == 'SECRETARY_FACULTY':
                    # Fakülte sekreteri - Fakülte seviyesinde yetki, bölüm seçimi YOK
                    faculty_id = request.POST.get('faculty')
                    if faculty_id:
                        try:
                            faculty = Faculty.objects.get(id=faculty_id)
                            user.faculty = faculty
                            user.department = None  # Fakülte sekreteri belirli bölümle ilişkili değil
                                
                        except Faculty.DoesNotExist:
                            messages.error(request, "Geçersiz fakülte seçimi.")
                            return render(request, 'auth/register.html', {
                                'form': form,
                                'faculties': Faculty.objects.all(),
                                'departments': Department.objects.select_related('faculty').all()
                            })
                    else:
                        messages.error(request, "Fakülte sekreteri için fakülte seçimi zorunludur.")
                        return render(request, 'auth/register.html', {
                            'form': form,
                            'faculties': Faculty.objects.all(),
                            'departments': Department.objects.select_related('faculty').all()
                        })
                        
                elif role == 'SECRETARY_DEPARTMENT':
                    # Bölüm sekreteri - Bölüm seviyesinde yetki, hem fakülte hem bölüm zorunlu
                    department_id = request.POST.get('department')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            user.department = department
                            user.faculty = department.faculty  # Otomatik fakülte ataması
                        except Department.DoesNotExist:
                            messages.error(request, "Geçersiz bölüm seçimi.")
                            return render(request, 'auth/register.html', {
                                'form': form,
                                'faculties': Faculty.objects.all(),
                                'departments': Department.objects.select_related('faculty').all()
                            })
                    else:
                        messages.error(request, "Bölüm sekreteri için bölüm seçimi zorunludur.")
                        return render(request, 'auth/register.html', {
                            'form': form,
                            'faculties': Faculty.objects.all(),
                            'departments': Department.objects.select_related('faculty').all()
                        })
                
                user.save()
                
                # Asistan ise profil oluştur
                if role == 'ASSISTANT':
                    department_id = request.POST.get('department')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            profile_data = {
                                'user': user,
                                'department': department,
                                'phone_number': request.POST.get('phone_number', ''),
                                'office_location': request.POST.get('office_location', ''),
                                'max_weekly_hours': request.POST.get('max_weekly_hours', 20),
                            }
                            AssistantProfile.objects.create(**profile_data)
                            
                            # Asistan için de fakülte/bölüm ataması
                            user.department = department
                            user.faculty = department.faculty
                            user.save()
                            
                        except Department.DoesNotExist:
                            messages.error(request, "Geçersiz bölüm seçimi.")
                            return render(request, 'auth/register.html', {
                                'form': form,
                                'faculties': Faculty.objects.all(),
                                'departments': Department.objects.select_related('faculty').all()
                            })
                    else:
                        messages.error(request, "Asistanlar için bölüm seçimi zorunludur.")
                        return render(request, 'auth/register.html', {
                            'form': form,
                            'faculties': Faculty.objects.all(),
                            'departments': Department.objects.select_related('faculty').all()
                        })
                
                messages.success(
                    request,
                    'Kayıt işleminiz başarıyla tamamlandı. Hesabınızın admin tarafından '
                    'onaylanmasını bekleyin. E-posta ile bilgilendirileceksiniz.'
                )
                
                # Log kaydı - yetki seviyesini göster
                permission_scope = user.get_permission_scope()
                logger.info(f"Yeni kullanıcı kaydı: {user.email} ({user.get_role_display()}) - Yetki: {permission_scope}")
                return redirect('login')
                
            except Exception as e:
                logger.error(f"Kayıt hatası: {str(e)}")
                messages.error(request, "Kayıt işlemi sırasında bir hata oluştu.")
        else:
            messages.error(request, "Lütfen formu doğru şekilde doldurun.")
    else:
        form = CustomUserCreationForm()
    
    # Form için gerekli veriler
    faculties = Faculty.objects.prefetch_related('departments').all()
    departments = Department.objects.select_related('faculty').all()
    
    return render(request, 'auth/register.html', {
        'form': form,
        'faculties': faculties,
        'departments': departments
    })
