# 🎓 Asistan Sınav Planlayıcı (Exam Planner) - Monolitik Yaklaşım

Üniversite sınavları için asistan gözetmen atama ve takvim yönetim sistemi.

## 📋 Özellikler

### 🔐 Rol Tabanlı Erişim Sistemi
- **👨‍💼 Admin**: Sistem yöneticisi - tüm yetkiler
- **🏛️ Rektörlük Sekreteri**: Tüm üniversite genelinde yetkili
- **🏫 Fakülte Sekreteri**: Fakülte seviyesinde yetkili
- **🏢 Bölüm Sekreteri**: Bölüm seviyesinde yetkili
- **👨‍🎓 Asistan**: Kişisel görev yönetimi

### 📊 Ana İşlevler
- **🎯 Sınav Yönetimi**: Sınav oluşturma, düzenleme ve takip
- **👥 Gözetmen Atama**: Asistanları sınavlara atama sistemi
- **📅 Takvim Yönetimi**: FullCalendar.js ile interaktif takvim
- **🔔 Bildirim Sistemi**: Görev atamaları ve onaylar
- **📈 İstatistikler**: Detaylı raporlama ve analiz

### 🏗️ Teknik Özellikler
- **🐍 Django 4.2.7**: Modern web framework
- **🎨 Bootstrap 5**: Responsive tasarım
- **📅 FullCalendar.js**: Takvim entegrasyonu
- **🗄️ SQLite**: Veritabanı
- **🔒 JWT Authentication**: Güvenli kimlik doğrulama
- **📱 Mobile-First**: Mobil uyumlu tasarım

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Django 4.2.7
- Git

### Kurulum Adımları

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/AtahanDuryaz/S-nav-Atama-Sistemi.git
cd S-nav-Atama-Sistemi
```

2. **Virtual environment oluşturun:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate     # Windows
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Veritabanını migrate edin:**
```bash
python manage.py migrate
```

5. **Test verilerini yükleyin (isteğe bağlı):**
```bash
python manage.py create_yeditepe_data
```

6. **Superuser oluşturun:**
```bash
python manage.py createsuperuser
```

7. **Sunucuyu çalıştırın:**
```bash
python manage.py runserver
```

## 👥 Kullanım

### 🔑 Test Hesapları (create_yeditepe_data komutu sonrası)

#### Adminler:
- **Email**: admin@yeditepe.edu.tr | **Şifre**: admin123
- **Email**: rektorluk.sekreter@yeditepe.edu.tr | **Şifre**: sekreter123

#### Asistanlar:
- **Email**: ahmet.yilmaz@yeditepe.edu.tr | **Şifre**: asistan123
- **Email**: pinar.erdem@yeditepe.edu.tr | **Şifre**: asistan123

### 📝 Kayıt İşlemi
1. `/auth/register/` sayfasından kayıt olun
2. Rolünüzü seçin (hiyerarşik yapıya göre)
3. Admin onayını bekleyin
4. E-posta ile bildirim alın

### 🎯 Ana İşlemler

#### Sekreterler İçin:
- Sınav oluşturma ve düzenleme
- Gözetmen ataması yapma
- Atama durumlarını takip etme
- İstatistikleri görüntüleme

#### Asistanlar İçin:
- Görev atamalarını görüntüleme
- Görevleri kabul/red etme
- Kişisel takvim yönetimi
- Etkinlik ekleme/düzenleme

## 🏗️ Proje Yapısı

```
exam_planner/           # Ana Django projesi
├── settings.py         # Django ayarları
├── urls.py            # Ana URL yapılandırması
└── wsgi.py            # WSGI yapılandırması

core/                  # Ana uygulama
├── models.py          # Veri modelleri
├── admin.py           # Django admin paneli
├── forms.py           # Form tanımları
├── views/             # Modüler views yapısı
│   ├── __init__.py    # Views export
│   ├── base.py        # Ortak imports
│   ├── base_views.py  # Dashboard views
│   ├── auth_views.py  # Kimlik doğrulama
│   ├── secretary_views.py  # Sekreter işlevleri
│   ├── assistant_views.py  # Asistan işlevleri
│   ├── calendar_views.py   # Takvim yönetimi
│   └── api_views.py   # AJAX endpoints
├── urls.py            # URL yapılandırması
└── management/        # Django komutları
    └── commands/
        └── create_yeditepe_data.py

templates/             # HTML şablonları
├── base.html          # Ana layout
├── auth/              # Kimlik doğrulama sayfaları
└── core/              # Uygulama sayfaları

static/                # CSS, JS, resimler
```

## 📊 Veri Modeli

### 👤 User (Özel kullanıcı modeli)
- Rol tabanlı yetkilendirme
- Email tabanlı giriş
- Fakülte/bölüm ilişkilendirme

### 🏫 Akademik Hiyerarşi
- **School**: Okul/Üniversite
- **Faculty**: Fakülte
- **Department**: Bölüm
- **Course**: Ders

### 📝 Sınav Yönetimi
- **Exam**: Sınav bilgileri
- **ProctorAssignment**: Gözetmen atamaları
- **CalendarEvent**: Takvim etkinlikleri

## 🔧 Geliştirme

### Views Yapısı
Modüler views yapısı kullanılmıştır:
- Her rol için ayrı dosyalar
- Ortak fonksiyonlar base.py'da
- API endpoints ayrı modülde

### Form Sistemi
- Rol bazlı dinamik formlar
- Hiyerarşik alan gösterimi
- AJAX ile dinamik yükleme

### Admin Panel
- Tüm modeller için özelleştirilmiş admin
- Bulk işlemler
- Gelişmiş filtreleme

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- Django Community
- Bootstrap Team
- FullCalendar.js Developers
- Font Awesome Icons

## 📞 İletişim

**Atahan Duryaz** - atahan@example.com

Proje Linki: [https://github.com/AtahanDuryaz/S-nav-Atama-Sistemi](https://github.com/AtahanDuryaz/S-nav-Atama-Sistemi)

---
⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!