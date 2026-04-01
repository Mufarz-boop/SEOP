from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user_model import UserModel
from app.models.admin_model import AdminModel
from app.models.teacher_model import TeacherModel
from app.models.student_model import StudentModel

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        # Redirect based on role
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'student':
            return redirect(url_for('student.dashboard'))
    
    if request.method == 'POST':
        register_number = request.form.get('register_number')
        password = request.form.get('password')
        
        if not register_number or not password:
            flash('Nomor registrasi dan password wajib diisi.', 'danger')
            return render_template('auth/login.html')
        
        user = UserModel.authenticate(register_number, password)
        
        if user:
            # Set session
            session['user_id'] = user['user_id']
            session['register_number'] = user['register_number']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['photo'] = user['photo']
            
            flash(f'Selamat datang, {user["full_name"]}!', 'success')
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('student.dashboard'))
        else:
            flash('Nomor registrasi atau password salah.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    role = session.get('role')
    
    user_details = UserModel.get_user_details(user_id)
    
    if role == 'admin':
        return redirect(url_for('admin.pengaturan'))
    elif role == 'teacher':
        return redirect(url_for('teacher.pengaturan'))
    elif role == 'student':
        return redirect(url_for('student.pengaturan'))
    
    return redirect(url_for('auth.login'))