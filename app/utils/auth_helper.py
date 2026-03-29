import bcrypt
import re
from datetime import datetime

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_register_number(role, birth_date_str):
    """Generate unique registration number based on role and birth date"""
    # Format: ROLE[YYYYMMDD][RANDOM]
    prefix_map = {
        'admin': 'AMN',
        'teacher': 'TCR',
        'student': 'SDT'
    }
    
    prefix = prefix_map.get(role, 'USR')
    
    # Parse birth date
    if birth_date_str:
        try:
            birth_date = datetime.strptime(str(birth_date_str), '%Y-%m-%d')
            date_part = birth_date.strftime('%Y%m%d')
        except:
            date_part = datetime.now().strftime('%Y%m%d')
    else:
        date_part = datetime.now().strftime('%Y%m%d')
    
    # Generate random suffix
    import random
    random_suffix = str(random.randint(1000, 9999))
    
    return f"{prefix}{date_part}{random_suffix}"

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_datetime(value, format='%d %B %Y %H:%M'):
    """Format datetime for templates"""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except:
                return value
    return value.strftime(format)

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    if isinstance(birth_date, str):
        try:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        except:
            return None
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age
