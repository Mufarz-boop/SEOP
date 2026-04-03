from app.database.db import execute_query
from app.utils.auth_helper import hash_password, verify_password, generate_register_number

class UserModel:
    @staticmethod
    def get_all_users():
        query = """
            SELECT u.*, 
                CASE 
                    WHEN u.role = 'admin' THEN a.gender
                    WHEN u.role = 'teacher' THEN t.gender
                    WHEN u.role = 'student' THEN s.gender
                END as gender,
                CASE 
                    WHEN u.role = 'admin' THEN a.phone_number
                    WHEN u.role = 'teacher' THEN t.phone_number
                    WHEN u.role = 'student' THEN s.phone_number
                END as phone_number
            FROM users u
            LEFT JOIN admin a ON u.user_id = a.user_id
            LEFT JOIN teachers t ON u.user_id = t.user_id
            LEFT JOIN students s ON u.user_id = s.user_id
            ORDER BY u.created_at DESC
        """
        return execute_query(query)
    
    @staticmethod
    def get_user_by_id(user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def get_user_by_register_number(register_number):
        query = "SELECT * FROM users WHERE register_number = %s"
        return execute_query(query, (register_number,), fetch_one=True)
    
    @staticmethod
    def get_user_by_username(username):
        query = "SELECT * FROM users WHERE username = %s"
        return execute_query(query, (username,), fetch_one=True)
    
    @staticmethod
    def authenticate(register_number, password):
        user = UserModel.get_user_by_register_number(register_number)
        if user and verify_password(password, user['password']):
            return user
        return None
    
    @staticmethod
    def create_user(register_number, password, full_name, role, username=None, photo='default_profile.jpeg'):
        hashed_password = hash_password(password)
        query = """
            INSERT INTO users (register_number, password, full_name, role, username, photo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (register_number, hashed_password, full_name, role, username, photo), commit=True)
    
    @staticmethod
    def update_user(user_id, full_name=None, username=None, photo=None):
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        if username:
            updates.append("username = %s")
            params.append(username)
        if photo:
            updates.append("photo = %s")
            params.append(photo)
        
        if not updates:
            return None
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        execute_query(query, tuple(params), commit=True)
        return UserModel.get_user_by_id(user_id)
    
    @staticmethod
    def update_password(user_id, new_password):
        hashed_password = hash_password(new_password)
        query = "UPDATE users SET password = %s WHERE user_id = %s"
        execute_query(query, (hashed_password, user_id), commit=True)
        return True
    
    @staticmethod
    def delete_user(user_id):
        query = "DELETE FROM users WHERE user_id = %s"
        execute_query(query, (user_id,), commit=True)
        return True
    
    @staticmethod
    def get_user_details(user_id):
        """Get user with role-specific details"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return None
        
        role = user['role']
        details = None
        
        if role == 'admin':
            query = """
                SELECT a.*, u.* FROM users u
                LEFT JOIN admin a ON u.user_id = a.user_id
                WHERE u.user_id = %s
            """
            details = execute_query(query, (user_id,), fetch_one=True)
        elif role == 'teacher':
            query = """
                SELECT t.*, u.*, s.subject_name 
                FROM users u
                LEFT JOIN teachers t ON u.user_id = t.user_id
                LEFT JOIN subjects s ON t.subject_id = s.subject_id
                WHERE u.user_id = %s
            """
            details = execute_query(query, (user_id,), fetch_one=True)
        elif role == 'student':
            query = """
                SELECT s.*, u.*, c.class_name, c.grade_level, m.major_name
                FROM users u
                LEFT JOIN students s ON u.user_id = s.user_id
                LEFT JOIN classes c ON s.class_id = c.class_id
                LEFT JOIN majors m ON s.major_id = m.major_id
                WHERE u.user_id = %s
            """
            details = execute_query(query, (user_id,), fetch_one=True)
        
        return details
    
    @staticmethod
    def get_users_by_role(role):
        query = """
            SELECT u.* FROM users u
            WHERE u.role = %s
            ORDER BY u.full_name ASC
        """
        return execute_query(query, (role,))
    
    @staticmethod
    def get_all_admins():
        """Get all admin users for report destination selection"""
        query = """
            SELECT u.user_id, u.full_name, u.register_number, a.position
            FROM users u
            JOIN admin a ON u.user_id = a.user_id
            WHERE u.role = 'admin' AND a.status = 'active'
            ORDER BY u.full_name ASC
        """
        return execute_query(query)