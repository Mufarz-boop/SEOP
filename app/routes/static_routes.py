from flask import Blueprint, render_template, send_from_directory, current_app
import os

bp = Blueprint('static_routes', __name__)

@bp.route('/')
def index():
    return render_template('auth/login.html')

@bp.route('/legal/privacy')
def privacy():
    return render_template('legal/privacy.html')

@bp.route('/legal/terms')
def terms():
    return render_template('legal/terms.html')

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)
