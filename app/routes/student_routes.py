from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session, current_app
import os
from werkzeug.utils import secure_filename
from app.utils.role_required import login_required, student_required
from app.utils.auth_helper import allowed_file
from app.models.user_model import UserModel
from app.models.student_model import StudentModel
from app.models.report_model import ReportModel

bp = Blueprint('student', __name__, url_prefix='/student')

# Dashboard
@bp.route('/dashboard')
@student_required
def dashboard():
    user_id = session.get('user_id')
    student = StudentModel.get_student_by_user_id(user_id)
    if not student:
        flash('Data siswa tidak ditemukan.', 'danger')
        return redirect(url_for('auth.logout'))
    
    stats = StudentModel.get_student_dashboard_stats(student['student_id'])
    return render_template('student/dashboard_student.html', stats=stats, student=student)

# ==================== LAPORAN ====================
@bp.route('/lapor', methods=['GET', 'POST'])
@student_required
def lapor():
    user_id = session.get('user_id')
    student = StudentModel.get_student_by_user_id(user_id)
    
    if request.method == 'POST':
        try:
            involved_student_id = request.form.get('student_id')
            title = request.form.get('title')
            description = request.form.get('description')
            violation_type_id = request.form.get('violation_type_id')
            admin_id = request.form.get('admin_id')  # Target admin
            
            if not all([involved_student_id, title, description, admin_id]):
                flash('Semua field wajib diisi.', 'danger')
                return redirect(url_for('student.lapor'))
            
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
                        return redirect(url_for('student.lapor'))
            
            # Create report
            ReportModel.create_report(
                reporter_id=user_id,
                student_id=involved_student_id,
                title=title,
                description=description,
                evidence_url=evidence_url,
                violation_type_id=violation_type_id if violation_type_id else None
            )
            
            flash('Laporan berhasil dikirim.', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    # Get data for form
    students = StudentModel.get_students_for_dropdown()
    violation_types = ReportModel.get_violation_types()
    admins = UserModel.get_all_admins()  # For selecting target admin
    
    return render_template('student/student_laporan.html',
                         students=students, 
                         violation_types=violation_types,
                         admins=admins,
                         student=student)

# ==================== LIHAT LAPORAN SAYA ====================
@bp.route('/laporan-saya')
@student_required
def laporan_saya():
    user_id = session.get('user_id')
    reports = ReportModel.get_reports_by_reporter(user_id)
    return render_template('student/laporan_saya.html', reports=reports)

# ==================== PERATURAN SEKOLAH ====================
@bp.route('/peraturan-sekolah')
@student_required
def peraturan_sekolah():
    violation_types = ReportModel.get_violation_types()
    return render_template('student/peraturan_sekolah_for_student.html', 
                         violation_types=violation_types)

# ==================== PENGATURAN ====================
@bp.route('/pengaturan', methods=['GET', 'POST'])
@student_required
def pengaturan():
    user_id = session.get('user_id')
    student = StudentModel.get_student_by_user_id(user_id)
    
    if request.method == 'POST':
        try:
            # Update user info
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            UserModel.update_user(user_id, full_name=full_name, username=username)
            
            # Update student info
            gender = request.form.get('gender')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            birth_date = request.form.get('birth_date')
            
            StudentModel.update_student(
                student_id=student['student_id'],
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
            return redirect(url_for('student.pengaturan'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('student/pengaturan_student.html', student=student)