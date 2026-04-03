from app.database.db import execute_query

class ReportModel:
    @staticmethod
    def get_all_reports():
        query = """
            SELECT r.*, 
                   u.full_name as reporter_name, u.role as reporter_role,
                   s.nis as student_nis, us.full_name as student_name,
                   c.class_name, vt.name as violation_type_name
            FROM reports r
            JOIN users u ON r.reporter_id = u.user_id
            LEFT JOIN students s ON r.student_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN violation_types vt ON r.violation_type_id = vt.id
            ORDER BY r.created_at DESC
        """
        return execute_query(query)
    
    @staticmethod
    def get_report_by_id(report_id):
        query = """
            SELECT r.*, 
                   u.full_name as reporter_name, u.role as reporter_role,
                   s.nis as student_nis, us.full_name as student_name,
                   c.class_name, vt.name as violation_type_name, vt.points as violation_points
            FROM reports r
            JOIN users u ON r.reporter_id = u.user_id
            LEFT JOIN students s ON r.student_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN violation_types vt ON r.violation_type_id = vt.id
            WHERE r.id = %s
        """
        return execute_query(query, (report_id,), fetch_one=True)
    
    @staticmethod
    def get_reports_by_reporter(reporter_id):
        """Get reports created by a specific user"""
        query = """
            SELECT r.*, 
                   s.nis as student_nis, us.full_name as student_name,
                   c.class_name, vt.name as violation_type_name
            FROM reports r
            LEFT JOIN students s ON r.student_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN violation_types vt ON r.violation_type_id = vt.id
            WHERE r.reporter_id = %s
            ORDER BY r.created_at DESC
        """
        return execute_query(query, (reporter_id,))
    
    @staticmethod
    def get_reports_for_admin(admin_id=None):
        """Get all reports (admin can see all)"""
        return ReportModel.get_all_reports()
    
    @staticmethod
    def create_report(reporter_id, student_id, title, description, 
                      evidence_url=None, violation_type_id=None, status='pending'):
        query = """
            INSERT INTO reports (reporter_id, student_id, title, description, 
                                evidence_url, violation_type_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (reporter_id, student_id, title, description,
                                     evidence_url, violation_type_id, status), commit=True)
    
    @staticmethod
    def update_report_status(report_id, status):
        """Update report status (pending, approved, rejected)"""
        query = "UPDATE reports SET status = %s WHERE id = %s"
        execute_query(query, (status, report_id), commit=True)
        return ReportModel.get_report_by_id(report_id)
    
    @staticmethod
    def delete_report(report_id):
        query = "DELETE FROM reports WHERE id = %s"
        execute_query(query, (report_id,), commit=True)
        return True
    
    @staticmethod
    def get_report_statistics():
        """Get report statistics for dashboard"""
        stats = {}
        
        # Total reports
        stats['total'] = execute_query(
            "SELECT COUNT(*) as count FROM reports", fetch_one=True
        )['count']
        
        # By status
        stats['pending'] = execute_query(
            "SELECT COUNT(*) as count FROM reports WHERE status = 'pending'", fetch_one=True
        )['count']
        
        stats['approved'] = execute_query(
            "SELECT COUNT(*) as count FROM reports WHERE status = 'approved'", fetch_one=True
        )['count']
        
        stats['rejected'] = execute_query(
            "SELECT COUNT(*) as count FROM reports WHERE status = 'rejected'", fetch_one=True
        )['count']

        # Reports by role
        query = """
            SELECT u.role, COUNT(*) as count
            FROM reports r
            JOIN users u ON r.reporter_id = u.user_id
            GROUP BY u.role
        """
        stats['by_role'] = execute_query(query)
        
        return stats
    
    @staticmethod
    def get_violation_types():
        """Get all violation types for dropdown"""
        query = "SELECT * FROM violation_types ORDER BY name ASC"
        return execute_query(query)
    
    @staticmethod
    def get_violation_type_by_id(violation_type_id):
        query = "SELECT * FROM violation_types WHERE id = %s"
        return execute_query(query, (violation_type_id,), fetch_one=True)
    
    @staticmethod
    def create_violation_type(name, description=None, points=0):
        query = """
            INSERT INTO violation_types (name, description, points)
            VALUES (%s, %s, %s)
        """
        return execute_query(query, (name, description, points), commit=True)
    
    @staticmethod
    def update_violation_type(violation_type_id, name=None, description=None, points=None):
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if points is not None:
            updates.append("points = %s")
            params.append(points)
        
        if not updates:
            return None
        
        params.append(violation_type_id)
        query = f"UPDATE violation_types SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), commit=True)
        return ReportModel.get_violation_type_by_id(violation_type_id)
    
    @staticmethod
    def delete_violation_type(violation_type_id):
        query = "DELETE FROM violation_types WHERE id = %s"
        execute_query(query, (violation_type_id,), commit=True)
        return True