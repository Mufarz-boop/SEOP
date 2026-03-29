# SEOP - School Environment Order Program

Aplikasi manajemen ketertiban dan kedisiplinan sekolah berbasis web menggunakan Flask.

## Fitur Utama

### Role-based Access Control
- **Admin**: Mengelola data murid, guru, kelas, jurusan, ekstrakurikuler, organisasi, akun, dan laporan
- **Teacher**: Melihat data murid dan kelas, membuat laporan pelanggaran
- **Student**: Membuat laporan pelanggaran, melihat peraturan sekolah

### Modul
1. **Dashboard** - Statistik dan informasi ringkasan untuk setiap role
2. **Data Murid** - Manajemen data siswa (CRUD untuk admin, view untuk teacher)
3. **Data Guru** - Manajemen data guru (CRUD untuk admin)
4. **Data Kelas** - Manajemen data kelas
5. **Data Jurusan** - Manajemen data jurusan
6. **Data Ekstrakurikuler** - Manajemen kegiatan ekstrakurikuler
7. **Data Organisasi** - Manajemen organisasi sekolah
8. **Kelola Akun** - Manajemen akun pengguna (admin only)
9. **Laporan** - Sistem pelaporan pelanggaran dengan upload file
10. **Peraturan Sekolah** - Daftar jenis pelanggaran dan poinnya

## Teknologi

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: Bootstrap 5, Jinja2 Templates
- **Security**: bcrypt password hashing, session-based authentication

## Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd seop
```

### 2. Buat Virtual Environment
```bash
python -m venv seop
source seop/bin/activate  # Linux/Mac
seop\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Database
1. Buat database MySQL baru dengan nama `db_core`
2. Import file SQL yang telah disediakan
3. Sesuaikan konfigurasi database di file `.env`

```env
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=db_core
MYSQL_PORT=3306
```

### 5. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## Struktur Proyek

```
seop/
├── app/
│   ├── database/
│   │   └── db.py              # Database connection
│   ├── models/
│   │   ├── user_model.py      # User model
│   │   ├── admin_model.py     # Admin model
│   │   ├── teacher_model.py   # Teacher model
│   │   ├── student_model.py   # Student model
│   │   ├── class_model.py     # Class model
│   │   ├── major_model.py     # Major model
│   │   ├── extracurricular_model.py
│   │   ├── organization_model.py
│   │   └── report_model.py    # Report & violation model
│   ├── routes/
│   │   ├── auth_routes.py     # Authentication routes
│   │   ├── admin_routes.py    # Admin routes
│   │   ├── teacher_routes.py  # Teacher routes
│   │   ├── student_routes.py  # Student routes
│   │   └── static_routes.py   # Static routes
│   ├── templates/
│   │   ├── admin/             # Admin templates
│   │   ├── teacher/           # Teacher templates
│   │   ├── student/           # Student templates
│   │   └── auth/              # Auth templates
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── uploads/           # File uploads
│   └── utils/
│       ├── auth_helper.py     # Authentication helpers
│       └── role_required.py   # Role decorators
├── config.py                  # Configuration
├── app.py                     # Application entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Default Login

Setelah import database, Anda dapat login dengan akun berikut:

| Role | Nomor Registrasi | Password |
|------|-----------------|----------|
| Admin | AMN1998122320250001 | admin123 |
| Teacher | TCR1993122400020000 | teacher123 |
| Student | SDT19861226000000000003 | student123 |

## Fitur Keamanan

- Password hashing menggunakan bcrypt
- Session-based authentication
- Role-based access control
- CSRF protection (via Flask-WTF)
- File upload validation

## Lisensi

MIT License
