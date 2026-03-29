from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import os
from werkzeug.utils import secure_filename
from app.utils.role_required import admin_required
from app.utils.auth_helper import allowed_file
from app.models.user_model import UserModel
from app.models.admin_model import AdminModel
from app.models.teacher_model import TeacherModel
from app.models.student_model import StudentModel
from app.models.class_model import ClassModel
from app.models.major_model import MajorModel
from app.models.extracurricular_model import ExtracurricularModel
from app.models.organization_model import OrganizationModel
from app.models.report_model import ReportModel
# ✅ IMPORT execute_query dari db.py (bukan get_db_connection!)
from app.database.db import execute_query

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Dashboard
@bp.route('/dashboard')
@admin_required
def dashboard():
    stats = AdminModel.get_dashboard_stats()
    return render_template('admin/dashboard_admin.html', stats=stats)

# ==================== DATA MURID ====================
@bp.route('/data-murid')
@admin_required
def data_murid():
    students = StudentModel.get_all_students()
    classes = ClassModel.get_all_classes()
    majors = MajorModel.get_all_majors()
    return render_template('admin/data_murid_admin.html', 
                         students=students, classes=classes, majors=majors)

@bp.route('/data-murid/tambah', methods=['POST'])
@admin_required
def tambah_murid():
    try:
        # Create user first
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        nis = request.form.get('nis')
        birth_date = request.form.get('birth_date')
        gender = request.form.get('gender')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        class_id = request.form.get('class_id')
        major_id = request.form.get('major_id')
        
        if not all([full_name, password, nis, father_name, mother_name]):
            flash('Semua field wajib diisi.', 'danger')
            return redirect(url_for('admin.data_murid'))
        
        # Generate register number
        from app.utils.auth_helper import generate_register_number
        register_number = generate_register_number('student', birth_date)
        
        # Create user
        user_id = UserModel.create_user(register_number, password, full_name, 'student', username)
        
        # Create student record
        StudentModel.create_student(
            user_id=user_id,
            nis=nis,
            birth_date=birth_date,
            gender=gender,
            address=address,
            phone_number=phone_number,
            father_name=father_name,
            mother_name=mother_name,
            class_id=class_id if class_id else None,
            major_id=major_id if major_id else None
        )
        
        flash('Data murid berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_murid'))

@bp.route('/data-murid/edit/<int:student_id>', methods=['POST'])
@admin_required
def edit_murid(student_id):
    try:
        student = StudentModel.get_student_by_id(student_id)
        if not student:
            flash('Data murid tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_murid'))
        
        nis = request.form.get('nis')
        birth_date = request.form.get('birth_date')
        gender = request.form.get('gender')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        class_id = request.form.get('class_id')
        major_id = request.form.get('major_id')
        status = request.form.get('status')
        
        StudentModel.update_student(
            student_id=student_id,
            nis=nis,
            birth_date=birth_date,
            gender=gender,
            address=address,
            phone_number=phone_number,
            father_name=father_name,
            mother_name=mother_name,
            class_id=class_id if class_id else None,
            major_id=major_id if major_id else None,
            status=status
        )
        
        # Update user info
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        if full_name or username:
            UserModel.update_user(student['user_id'], full_name=full_name, username=username)
        
        flash('Data murid berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_murid'))

@bp.route('/data-murid/hapus/<int:student_id>', methods=['POST'])
@admin_required
def hapus_murid(student_id):
    try:
        student = StudentModel.get_student_by_id(student_id)
        if not student:
            flash('Data murid tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_murid'))
        
        StudentModel.delete_student(student_id)
        UserModel.delete_user(student['user_id'])
        
        flash('Data murid berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_murid'))

# ==================== DATA GURU ====================
@bp.route('/data-guru')
@admin_required
def data_guru():
    teachers = TeacherModel.get_all_teachers()
    
    # ✅ PAKAI execute_query() yang udah ada di db.py! Simple kan?
    try:
        subjects = execute_query("SELECT * FROM subjects ORDER BY subject_name ASC")
    except Exception as e:
        subjects = []
        flash(f'Gagal mengambil data mata pelajaran: {str(e)}', 'warning')
    
    return render_template('admin/data_guru_admin.html', teachers=teachers, subjects=subjects)

@bp.route('/data-guru/tambah', methods=['POST'])
@admin_required
def tambah_guru():
    try:
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        nip = request.form.get('nip')
        birth_date = request.form.get('birth_date')
        gender = request.form.get('gender')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        department = request.form.get('department')
        subject_id = request.form.get('subject_id')
        
        if not all([full_name, password, nip]):
            flash('Nama lengkap, password, dan NIP wajib diisi.', 'danger')
            return redirect(url_for('admin.data_guru'))
        
        # Generate register number
        from app.utils.auth_helper import generate_register_number
        register_number = generate_register_number('teacher', birth_date)
        
        # Create user
        user_id = UserModel.create_user(register_number, password, full_name, 'teacher', username)
        
        # Create teacher record
        TeacherModel.create_teacher(
            user_id=user_id,
            nip=nip,
            gender=gender,
            birth_date=birth_date,
            phone_number=phone_number,
            address=address,
            department=department or 'Akademik',
            subject_id=subject_id if subject_id else None
        )
        
        flash('Data guru berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_guru'))

@bp.route('/data-guru/edit/<int:teacher_id>', methods=['POST'])
@admin_required
def edit_guru(teacher_id):
    try:
        teacher = TeacherModel.get_teacher_by_id(teacher_id)
        if not teacher:
            flash('Data guru tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_guru'))
        
        nip = request.form.get('nip')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        department = request.form.get('department')
        subject_id = request.form.get('subject_id')
        status = request.form.get('status')
        
        TeacherModel.update_teacher(
            teacher_id=teacher_id,
            nip=nip,
            gender=gender,
            birth_date=birth_date,
            phone_number=phone_number,
            address=address,
            department=department,
            subject_id=subject_id if subject_id else None,
            status=status
        )
        
        # Update user info
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        if full_name or username:
            UserModel.update_user(teacher['user_id'], full_name=full_name, username=username)
        
        flash('Data guru berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_guru'))

@bp.route('/data-guru/hapus/<int:teacher_id>', methods=['POST'])
@admin_required
def hapus_guru(teacher_id):
    try:
        teacher = TeacherModel.get_teacher_by_id(teacher_id)
        if not teacher:
            flash('Data guru tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_guru'))
        
        TeacherModel.delete_teacher(teacher_id)
        UserModel.delete_user(teacher['user_id'])
        
        flash('Data guru berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_guru'))

# ==================== DATA KELAS ====================
@bp.route('/data-kelas')
@admin_required
def data_kelas():
    classes = ClassModel.get_all_classes()
    majors = MajorModel.get_all_majors()
    teachers = TeacherModel.get_teachers_for_dropdown()
    return render_template('admin/data_kelas_admin.html', classes=classes, majors=majors, teachers=teachers)

@bp.route('/data-kelas/tambah', methods=['POST'])
@admin_required
def tambah_kelas():
    try:
        class_name = request.form.get('class_name')
        grade_level = request.form.get('grade_level')
        major_id = request.form.get('major_id')
        academic_year = request.form.get('academic_year', '2025/2026')
        capacity = request.form.get('capacity', 30)
        room_number = request.form.get('room_number')
        homeroom_teacher_id = request.form.get('homeroom_teacher_id')
        
        if not all([class_name, grade_level]):
            flash('Nama kelas dan tingkat wajib diisi.', 'danger')
            return redirect(url_for('admin.data_kelas'))
        
        ClassModel.create_class(
            class_name=class_name,
            grade_level=grade_level,
            major_id=major_id if major_id else None,
            academic_year=academic_year,
            capacity=int(capacity),
            room_number=room_number,
            homeroom_teacher_id=homeroom_teacher_id if homeroom_teacher_id else None
        )
        
        flash('Data kelas berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_kelas'))

@bp.route('/data-kelas/edit/<int:class_id>', methods=['POST'])
@admin_required
def edit_kelas(class_id):
    try:
        cls = ClassModel.get_class_by_id(class_id)
        if not cls:
            flash('Data kelas tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_kelas'))
        
        class_name = request.form.get('class_name')
        grade_level = request.form.get('grade_level')
        major_id = request.form.get('major_id')
        academic_year = request.form.get('academic_year')
        capacity = request.form.get('capacity')
        room_number = request.form.get('room_number')
        homeroom_teacher_id = request.form.get('homeroom_teacher_id')
        status = request.form.get('status')
        
        ClassModel.update_class(
            class_id=class_id,
            class_name=class_name,
            grade_level=grade_level,
            major_id=major_id if major_id else None,
            academic_year=academic_year,
            capacity=int(capacity) if capacity else None,
            room_number=room_number,
            homeroom_teacher_id=homeroom_teacher_id if homeroom_teacher_id else None,
            status=status
        )
        
        flash('Data kelas berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_kelas'))

@bp.route('/data-kelas/hapus/<int:class_id>', methods=['POST'])
@admin_required
def hapus_kelas(class_id):
    try:
        cls = ClassModel.get_class_by_id(class_id)
        if not cls:
            flash('Data kelas tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_kelas'))
        
        ClassModel.delete_class(class_id)
        flash('Data kelas berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_kelas'))

# ==================== DATA JURUSAN ====================
@bp.route('/data-jurusan')
@admin_required
def data_jurusan():
    majors = MajorModel.get_all_majors()
    teachers = TeacherModel.get_teachers_for_dropdown()
    return render_template('admin/data_jurusan_admin.html', majors=majors, teachers=teachers)

@bp.route('/data-jurusan/tambah', methods=['POST'])
@admin_required
def tambah_jurusan():
    try:
        major_name = request.form.get('major_name')
        description = request.form.get('description')
        head_of_major_id = request.form.get('head_of_major_id')
        established_year = request.form.get('established_year')
        
        if not major_name:
            flash('Nama jurusan wajib diisi.', 'danger')
            return redirect(url_for('admin.data_jurusan'))
        
        MajorModel.create_major(
            major_name=major_name,
            description=description,
            head_of_major_id=head_of_major_id if head_of_major_id else None,
            established_year=established_year if established_year else None
        )
        
        flash('Data jurusan berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_jurusan'))

@bp.route('/data-jurusan/edit/<int:major_id>', methods=['POST'])
@admin_required
def edit_jurusan(major_id):
    try:
        major = MajorModel.get_major_by_id(major_id)
        if not major:
            flash('Data jurusan tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_jurusan'))
        
        major_name = request.form.get('major_name')
        description = request.form.get('description')
        head_of_major_id = request.form.get('head_of_major_id')
        established_year = request.form.get('established_year')
        status = request.form.get('status')
        
        MajorModel.update_major(
            major_id=major_id,
            major_name=major_name,
            description=description,
            head_of_major_id=head_of_major_id if head_of_major_id else None,
            established_year=established_year if established_year else None,
            status=status
        )
        
        flash('Data jurusan berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_jurusan'))

@bp.route('/data-jurusan/hapus/<int:major_id>', methods=['POST'])
@admin_required
def hapus_jurusan(major_id):
    try:
        major = MajorModel.get_major_by_id(major_id)
        if not major:
            flash('Data jurusan tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_jurusan'))
        
        MajorModel.delete_major(major_id)
        flash('Data jurusan berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_jurusan'))

# ==================== DATA EKSTRAKURIKULER ====================
@bp.route('/data-ekstrakurikuler')
@admin_required
def data_ekstrakurikuler():
    extracurriculars = ExtracurricularModel.get_all_extracurriculars()
    teachers = TeacherModel.get_teachers_for_dropdown()
    students = StudentModel.get_students_for_dropdown()
    return render_template('admin/data_ekstrakurikuler_admin.html', 
                         extracurriculars=extracurriculars, teachers=teachers, students=students)

@bp.route('/data-ekstrakurikuler/tambah', methods=['POST'])
@admin_required
def tambah_ekstrakurikuler():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        supervisor_teacher_id = request.form.get('supervisor_teacher_id')
        student_leader_id = request.form.get('student_leader_id')
        schedule_day = request.form.get('schedule_day')
        schedule_time = request.form.get('schedule_time')
        location = request.form.get('location')
        
        if not name:
            flash('Nama ekstrakurikuler wajib diisi.', 'danger')
            return redirect(url_for('admin.data_ekstrakurikuler'))
        
        ExtracurricularModel.create_extracurricular(
            name=name,
            description=description,
            supervisor_teacher_id=supervisor_teacher_id if supervisor_teacher_id else None,
            student_leader_id=student_leader_id if student_leader_id else None,
            schedule_day=schedule_day,
            schedule_time=schedule_time,
            location=location
        )
        
        flash('Data ekstrakurikuler berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_ekstrakurikuler'))

@bp.route('/data-ekstrakurikuler/edit/<int:extracurricular_id>', methods=['POST'])
@admin_required
def edit_ekstrakurikuler(extracurricular_id):
    try:
        extracurricular = ExtracurricularModel.get_extracurricular_by_id(extracurricular_id)
        if not extracurricular:
            flash('Data ekstrakurikuler tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_ekstrakurikuler'))
        
        name = request.form.get('name')
        description = request.form.get('description')
        supervisor_teacher_id = request.form.get('supervisor_teacher_id')
        student_leader_id = request.form.get('student_leader_id')
        schedule_day = request.form.get('schedule_day')
        schedule_time = request.form.get('schedule_time')
        location = request.form.get('location')
        status = request.form.get('status')
        
        ExtracurricularModel.update_extracurricular(
            extracurricular_id=extracurricular_id,
            name=name,
            description=description,
            supervisor_teacher_id=supervisor_teacher_id if supervisor_teacher_id else None,
            student_leader_id=student_leader_id if student_leader_id else None,
            schedule_day=schedule_day,
            schedule_time=schedule_time,
            location=location,
            status=status
        )
        
        flash('Data ekstrakurikuler berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_ekstrakurikuler'))

@bp.route('/data-ekstrakurikuler/hapus/<int:extracurricular_id>', methods=['POST'])
@admin_required
def hapus_ekstrakurikuler(extracurricular_id):
    try:
        extracurricular = ExtracurricularModel.get_extracurricular_by_id(extracurricular_id)
        if not extracurricular:
            flash('Data ekstrakurikuler tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_ekstrakurikuler'))
        
        ExtracurricularModel.delete_extracurricular(extracurricular_id)
        flash('Data ekstrakurikuler berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_ekstrakurikuler'))

# ==================== DATA ORGANISASI ====================
@bp.route('/data-organisasi')
@admin_required
def data_organisasi():
    organizations = OrganizationModel.get_all_organizations()
    teachers = TeacherModel.get_teachers_for_dropdown()
    students = StudentModel.get_students_for_dropdown()
    return render_template('admin/data_organisasi_admin.html',
                         organizations=organizations, teachers=teachers, students=students)

@bp.route('/data-organisasi/tambah', methods=['POST'])
@admin_required
def tambah_organisasi():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        supervisor_teacher_id = request.form.get('supervisor_teacher_id')
        president_student_id = request.form.get('president_student_id')
        meeting_day = request.form.get('meeting_day')
        meeting_time = request.form.get('meeting_time')
        location = request.form.get('location')
        
        if not name:
            flash('Nama organisasi wajib diisi.', 'danger')
            return redirect(url_for('admin.data_organisasi'))
        
        OrganizationModel.create_organization(
            name=name,
            description=description,
            supervisor_teacher_id=supervisor_teacher_id if supervisor_teacher_id else None,
            president_student_id=president_student_id if president_student_id else None,
            meeting_day=meeting_day,
            meeting_time=meeting_time,
            location=location
        )
        
        flash('Data organisasi berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_organisasi'))

@bp.route('/data-organisasi/edit/<int:organization_id>', methods=['POST'])
@admin_required
def edit_organisasi(organization_id):
    try:
        organization = OrganizationModel.get_organization_by_id(organization_id)
        if not organization:
            flash('Data organisasi tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_organisasi'))
        
        name = request.form.get('name')
        description = request.form.get('description')
        supervisor_teacher_id = request.form.get('supervisor_teacher_id')
        president_student_id = request.form.get('president_student_id')
        meeting_day = request.form.get('meeting_day')
        meeting_time = request.form.get('meeting_time')
        location = request.form.get('location')
        status = request.form.get('status')
        
        OrganizationModel.update_organization(
            organization_id=organization_id,
            name=name,
            description=description,
            supervisor_teacher_id=supervisor_teacher_id if supervisor_teacher_id else None,
            president_student_id=president_student_id if president_student_id else None,
            meeting_day=meeting_day,
            meeting_time=meeting_time,
            location=location,
            status=status
        )
        
        flash('Data organisasi berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_organisasi'))

@bp.route('/data-organisasi/hapus/<int:organization_id>', methods=['POST'])
@admin_required
def hapus_organisasi(organization_id):
    try:
        organization = OrganizationModel.get_organization_by_id(organization_id)
        if not organization:
            flash('Data organisasi tidak ditemukan.', 'danger')
            return redirect(url_for('admin.data_organisasi'))
        
        OrganizationModel.delete_organization(organization_id)
        flash('Data organisasi berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.data_organisasi'))

# ==================== KELOLA AKUN ====================
@bp.route('/kelola-akun')
@admin_required
def kelola_akun():
    users = UserModel.get_all_users()
    return render_template('admin/admin_akun.html', users=users)

@bp.route('/kelola-akun/tambah', methods=['POST'])
@admin_required
def tambah_akun():
    try:
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        birth_date = request.form.get('birth_date')
        
        if not all([full_name, password, role]):
            flash('Nama lengkap, password, dan role wajib diisi.', 'danger')
            return redirect(url_for('admin.kelola_akun'))
        
        # Generate register number
        from app.utils.auth_helper import generate_register_number
        register_number = generate_register_number(role, birth_date)
        
        # Create user
        user_id = UserModel.create_user(register_number, password, full_name, role, username)
        
        # Create role-specific record
        if role == 'admin':
            AdminModel.create_admin(user_id=user_id)
        elif role == 'teacher':
            TeacherModel.create_teacher(user_id=user_id, nip='TEMP' + str(user_id))
        elif role == 'student':
            StudentModel.create_student(user_id=user_id, nis='TEMP' + str(user_id),
                                        father_name='Temp', mother_name='Temp')
        
        flash('Akun berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.kelola_akun'))

@bp.route('/kelola-akun/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_akun(user_id):
    try:
        user = UserModel.get_user_by_id(user_id)
        if not user:
            flash('Akun tidak ditemukan.', 'danger')
            return redirect(url_for('admin.kelola_akun'))
        
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        
        UserModel.update_user(user_id=user_id, full_name=full_name, username=username)
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            UserModel.update_password(user_id, new_password)
        
        flash('Akun berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.kelola_akun'))

@bp.route('/kelola-akun/hapus/<int:user_id>', methods=['POST'])
@admin_required
def hapus_akun(user_id):
    try:
        user = UserModel.get_user_by_id(user_id)
        if not user:
            flash('Akun tidak ditemukan.', 'danger')
            return redirect(url_for('admin.kelola_akun'))
        
        # Cannot delete own account
        if user_id == session.get('user_id'):
            flash('Anda tidak dapat menghapus akun sendiri.', 'danger')
            return redirect(url_for('admin.kelola_akun'))
        
        UserModel.delete_user(user_id)
        flash('Akun berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.kelola_akun'))

# ==================== LAPORAN PENGGUNA ====================
@bp.route('/laporan-pengguna')
@admin_required
def laporan_pengguna():
    reports = ReportModel.get_all_reports()
    violation_types = ReportModel.get_violation_types()
    return render_template('admin/laporan_pengguna.html', reports=reports, violation_types=violation_types)

@bp.route('/laporan-pengguna/update-status/<int:report_id>', methods=['POST'])
@admin_required
def update_status_laporan(report_id):
    try:
        status = request.form.get('status')
        if status not in ['pending', 'approved', 'rejected']:
            flash('Status tidak valid.', 'danger')
            return redirect(url_for('admin.laporan_pengguna'))
        
        ReportModel.update_report_status(report_id, status)
        flash(f'Status laporan berhasil diubah menjadi {status}.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.laporan_pengguna'))

# ==================== PERATURAN SEKOLAH ====================
@bp.route('/peraturan-sekolah')
@admin_required
def peraturan_sekolah():
    violation_types = ReportModel.get_violation_types()
    return render_template('admin/peraturan_sekolah_for_admin.html', violation_types=violation_types)

@bp.route('/peraturan-sekolah/tambah', methods=['POST'])
@admin_required
def tambah_peraturan():
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        points = request.form.get('points', 0)
        
        if not name:
            flash('Nama pelanggaran wajib diisi.', 'danger')
            return redirect(url_for('admin.peraturan_sekolah'))
        
        ReportModel.create_violation_type(name, description, int(points))
        flash('Jenis pelanggaran berhasil ditambahkan.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.peraturan_sekolah'))

@bp.route('/peraturan-sekolah/edit/<int:violation_type_id>', methods=['POST'])
@admin_required
def edit_peraturan(violation_type_id):
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        points = request.form.get('points')
        
        ReportModel.update_violation_type(
            violation_type_id=violation_type_id,
            name=name,
            description=description,
            points=int(points) if points else None
        )
        flash('Jenis pelanggaran berhasil diperbarui.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.peraturan_sekolah'))

@bp.route('/peraturan-sekolah/hapus/<int:violation_type_id>', methods=['POST'])
@admin_required
def hapus_peraturan(violation_type_id):
    try:
        ReportModel.delete_violation_type(violation_type_id)
        flash('Jenis pelanggaran berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.peraturan_sekolah'))

# ==================== PENGATURAN ====================
@bp.route('/pengaturan', methods=['GET', 'POST'])
@admin_required
def pengaturan():
    user_id = session.get('user_id')
    admin = AdminModel.get_admin_by_user_id(user_id)
    
    if request.method == 'POST':
        try:
            # Update user info
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            UserModel.update_user(user_id, full_name=full_name, username=username)
            
            # Update admin info
            gender = request.form.get('gender')
            phone_number = request.form.get('phone_number')
            address = request.form.get('address')
            birth_date = request.form.get('birth_date')
            position = request.form.get('position')
            
            AdminModel.update_admin(
                admin_id=admin['admin_id'],
                gender=gender,
                phone_number=phone_number,
                address=address,
                birth_date=birth_date,
                position=position
            )
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                UserModel.update_password(user_id, new_password)
            
            # Update session
            session['full_name'] = full_name
            
            flash('Profil berhasil diperbarui.', 'success')
            return redirect(url_for('admin.pengaturan'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('admin/pengaturan_admin.html', admin=admin)