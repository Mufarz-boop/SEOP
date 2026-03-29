from app.database.db import execute_query

class AdminModel:
    @staticmethod
    def get_all_admins():
        query = """
            SELECT a.*, u.full_name, u.register_number, u.username, u.photo, u.created_at as user_created_at
            FROM admin a
            JOIN users u ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
        """
        return execute_query(query)
    
    @staticmethod
    def get_admin_by_id(admin_id):
        query = """
            SELECT a.*, u.full_name, u.register_number, u.username, u.photo
            FROM admin a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.admin_id = %s
        """
        return execute_query(query, (admin_id,), fetch_one=True)
    
    @staticmethod
    def get_admin_by_user_id(user_id):
        query = """
            SELECT a.*, u.full_name, u.register_number, u.username, u.photo
            FROM admin a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.user_id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def create_admin(user_id, gender=None, phone_number=None, address=None, 
                     birth_date=None, position=None, status='active'):
        query = """
            INSERT INTO admin (user_id, gender, phone_number, address, birth_date, position, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (user_id, gender, phone_number, address, birth_date, position, status), commit=True)
    
    @staticmethod
    def update_admin(admin_id, gender=None, phone_number=None, address=None, 
                     birth_date=None, position=None, status=None):
        updates = []
        params = []
        
        if gender:
            updates.append("gender = %s")
            params.append(gender)
        if phone_number:
            updates.append("phone_number = %s")
            params.append(phone_number)
        if address:
            updates.append("address = %s")
            params.append(address)
        if birth_date:
            updates.append("birth_date = %s")
            params.append(birth_date)
        if position:
            updates.append("position = %s")
            params.append(position)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(admin_id)
        query = f"UPDATE admin SET {', '.join(updates)} WHERE admin_id = %s"
        execute_query(query, tuple(params), commit=True)
        return AdminModel.get_admin_by_id(admin_id)
    
    @staticmethod
    def delete_admin(admin_id):
        query = "DELETE FROM admin WHERE admin_id = %s"
        execute_query(query, (admin_id,), commit=True)
        return True
    
    @staticmethod
    def get_dashboard_stats():
        """Get statistics for admin dashboard"""
        stats = {}
        
        # Total counts
        stats['total_students'] = execute_query("SELECT COUNT(*) as count FROM students", fetch_one=True)['count']
        stats['total_teachers'] = execute_query("SELECT COUNT(*) as count FROM teachers", fetch_one=True)['count']
        stats['total_admins'] = execute_query("SELECT COUNT(*) as count FROM admin", fetch_one=True)['count']
        stats['total_classes'] = execute_query("SELECT COUNT(*) as count FROM classes", fetch_one=True)['count']
        stats['total_majors'] = execute_query("SELECT COUNT(*) as count FROM majors", fetch_one=True)['count']
        stats['total_extracurriculars'] = execute_query("SELECT COUNT(*) as count FROM extracurriculars", fetch_one=True)['count']
        stats['total_organizations'] = execute_query("SELECT COUNT(*) as count FROM school_organizations", fetch_one=True)['count']
        
        # Pending reports
        stats['pending_reports'] = execute_query(
            "SELECT COUNT(*) as count FROM reports WHERE status = 'pending'", 
            fetch_one=True
        )['count']
        
        # Recent reports
        stats['recent_reports'] = execute_query("""
            SELECT r.*, u.full_name as reporter_name, s.nis as student_nis
            FROM reports r
            JOIN users u ON r.reporter_id = u.user_id
            LEFT JOIN students s ON r.student_id = s.student_id
            ORDER BY r.created_at DESC
            LIMIT 5
        """)
        
        return stats
