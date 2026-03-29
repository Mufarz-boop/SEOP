from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import os
from werkzeug.utils import secure_filename
from app.utils.role_required import teacher_required
from app.utils.auth_helper import allowed_file
from app.models.user_model import UserModel
from app.models.teacher_model import TeacherModel
from app.models.student_model import StudentModel
from app.models.class_model import ClassModel
from app.models.report_model import ReportModel
# ✅ TAMBAH INI: Import execute_query dari db.py
from app.database.db import execute_query

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# Dashboard
@bp.route('/dashboard')
@teacher_required
def dashboard():
    user_id = session.get('user_id')
    teacher = TeacherModel.get_teacher_by_user_id(user_id)
    if not teacher:
        flash('Data guru tidak ditemukan.', 'danger')
        return redirect(url_for('auth.logout'))
    
    stats = TeacherModel.get_teacher_dashboard_stats(teacher['teacher_id'])
    return render_template('teacher/dashboard_teacher.html', stats=stats, teacher=teacher)

# ==================== DATA MURID (VIEW ONLY) ====================
@bp.route('/data-murid')
@teacher_required
def data_murid():
    students = StudentModel.get_all_students()
    classes = ClassModel.get_all_classes()
    # ✅ GANTI INI: Dari ReportModel.execute_query() jadi execute_query() langsung
    majors = execute_query("SELECT * FROM majors ORDER BY major_name ASC")
    return render_template('teacher/data_murid_teacher.html', 
                         students=students, classes=classes, majors=majors)

@bp.route('/data-murid/detail/<int:student_id>')
@teacher_required
def detail_murid(student_id):
    student = StudentModel.get_student_by_id(student_id)
    if not student:
        flash('Data murid tidak ditemukan.', 'danger')
        return redirect(url_for('teacher.data_murid'))
    
    violations = StudentModel.get_student_violations(student_id)
    extracurriculars = StudentModel.get_student_extracurriculars(student_id)
    
    # Redirect ke list murid dengan flash message
    flash(f'Detail murid {student["full_name"]} berhasil diakses.', 'success')
    return redirect(url_for('teacher.data_murid'))

# ==================== DATA KELAS (VIEW ONLY) ====================
@bp.route('/data-kelas')
@teacher_required
def data_kelas():
    user_id = session.get('user_id')
    teacher = TeacherModel.get_teacher_by_user_id(user_id)
    
    # Get homeroom classes
    homeroom_classes = TeacherModel.get_homeroom_classes(teacher['teacher_id'])
    all_classes = ClassModel.get_all_classes()
    
    return render_template('teacher/data_kelas_teacher.html',
                         homeroom_classes=homeroom_classes, all_classes=all_classes, teacher=teacher)

@bp.route('/data-kelas/detail/<int:class_id>')
@teacher_required
def detail_kelas(class_id):
    cls = ClassModel.get_class_by_id(class_id)
    if not cls:
        flash('Data kelas tidak ditemukan.', 'danger')
        return redirect(url_for('teacher.data_kelas'))
    
    students = StudentModel.get_students_by_class(class_id)
    
    # Ambil data yang sama kayak data_kelas
    user_id = session.get('user_id')
    teacher = TeacherModel.get_teacher_by_user_id(user_id)
    homeroom_classes = TeacherModel.get_homeroom_classes(teacher['teacher_id'])
    all_classes = ClassModel.get_all_classes()
    
    # Render template yang sama, tapi kasih flag selected_class
    return render_template('teacher/data_kelas_teacher.html',
                         homeroom_classes=homeroom_classes, 
                         all_classes=all_classes, 
                         teacher=teacher,
                         selected_class=cls,      # Kelas yang dipilih
                         students=students,       # Murid di kelas itu
                         show_detail=True)        # Flag buat tampilkan detail

# ==================== LAPORAN ====================
@bp.route('/lapor', methods=['GET', 'POST'])
@teacher_required
def lapor():
    user_id = session.get('user_id')
    teacher = TeacherModel.get_teacher_by_user_id(user_id)
    
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            title = request.form.get('title')
            description = request.form.get('description')
            violation_type_id = request.form.get('violation_type_id')
            admin_id = request.form.get('admin_id')  # Target admin
            
            if not all([student_id, title, description, admin_id]):
                flash('Semua field wajib diisi.', 'danger')
                return redirect(url_for('teacher.lapor'))
            
            # Handle file upload
            evidence_url = None
            if 'evidence' in request.files:
                file = request.files['evidence']
                if file and file.filename:
                    if allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                        filename = secure_filename(file.filename)
                        # Determine subfolder based on file type
                        ext = filename.rsplit('.', 1)[1].lower()
                        if ext in ['mp4']:
                            subfolder = 'videos'
                        elif ext in ['mp3', 'wav']:
                            subfolder = 'audio'
                        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                            subfolder = 'images'
                        else:
                            subfolder = 'documents'
                        
                        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
                        os.makedirs(upload_path, exist_ok=True)
                        
                        file_path = os.path.join(upload_path, filename)
                        file.save(file_path)
                        evidence_url = f'uploads/{subfolder}/{filename}'
                    else:
                        flash('Format file tidak didukung.', 'danger')
                        return redirect(url_for('teacher.lapor'))
            
            # Create report
            ReportModel.create_report(
                reporter_id=user_id,
                student_id=student_id,
                title=title,
                description=description,
                evidence_url=evidence_url,
                violation_type_id=violation_type_id if violation_type_id else None
            )
            
            flash('Laporan berhasil dikirim.', 'success')
            return redirect(url_for('teacher.dashboard'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    # Get data for form
    students = StudentModel.get_students_for_dropdown()
    violation_types = ReportModel.get_violation_types()
    admins = UserModel.get_all_admins()  # For selecting target admin
    
    return render_template('teacher/teacher_laporan.html',
                         students=students, 
                         violation_types=violation_types,
                         admins=admins,
                         teacher=teacher)

# ==================== PERATURAN SEKOLAH ====================
@bp.route('/peraturan-sekolah')
@teacher_required
def peraturan_sekolah():
    violation_types = ReportModel.get_violation_types()
    return render_template('teacher/peraturan_sekolah_for_teacher.html', 
                         violation_types=violation_types)

# ==================== PENGATURAN ====================
@bp.route('/pengaturan', methods=['GET', 'POST'])
@teacher_required
def pengaturan():
    user_id = session.get('user_id')
    teacher = TeacherModel.get_teacher_by_user_id(user_id)
    
    if request.method == 'POST':
        try:
            # Update user info
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            UserModel.update_user(user_id, full_name=full_name, username=username)
            
            # Update teacher info
            gender = request.form.get('gender')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            birth_date = request.form.get('birth_date')
            
            TeacherModel.update_teacher(
                teacher_id=teacher['teacher_id'],
                gender=gender,
                phone_number=phone_number,
                address=address,
                birth_date=birth_date
            )
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                UserModel.update_password(user_id, new_password)
            
            # Update session
            session['full_name'] = full_name
            
            flash('Profil berhasil diperbarui.', 'success')
            return redirect(url_for('teacher.pengaturan'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('teacher/pengaturan_teacher.html', teacher=teacher)