from app.database.db import execute_query

class MajorModel:
    @staticmethod
    def get_all_majors():
        query = """
            SELECT m.*, u.full_name as head_of_major_name
            FROM majors m
            LEFT JOIN teachers t ON m.head_of_major_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            ORDER BY m.major_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_major_by_id(major_id):
        query = """
            SELECT m.*, u.full_name as head_of_major_name
            FROM majors m
            LEFT JOIN teachers t ON m.head_of_major_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE m.major_id = %s
        """
        return execute_query(query, (major_id,), fetch_one=True)
    
    @staticmethod
    def create_major(major_name, description=None, head_of_major_id=None, 
                     established_year=None, status='active'):
        query = """
            INSERT INTO majors (major_name, description, head_of_major_id, established_year, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (major_name, description, head_of_major_id, 
                                     established_year, status), commit=True)
    
    @staticmethod
    def update_major(major_id, major_name=None, description=None, head_of_major_id=None,
                     established_year=None, status=None):
        updates = []
        params = []
        
        if major_name:
            updates.append("major_name = %s")
            params.append(major_name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if head_of_major_id is not None:
            updates.append("head_of_major_id = %s")
            params.append(head_of_major_id)
        if established_year:
            updates.append("established_year = %s")
            params.append(established_year)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(major_id)
        query = f"UPDATE majors SET {', '.join(updates)} WHERE major_id = %s"
        execute_query(query, tuple(params), commit=True)
        return MajorModel.get_major_by_id(major_id)
    
    @staticmethod
    def delete_major(major_id):
        query = "DELETE FROM majors WHERE major_id = %s"
        execute_query(query, (major_id,), commit=True)
        return True
    
    @staticmethod
    def get_majors_for_dropdown():
        query = """
            SELECT major_id, major_name
            FROM majors
            WHERE status = 'active'
            ORDER BY major_name ASC
        """
        return execute_query(query)
