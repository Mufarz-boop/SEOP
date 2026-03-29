from app.database.db import execute_query

class ExtracurricularModel:
    @staticmethod
    def get_all_extracurriculars():
        query = """
            SELECT e.*, u.full_name as supervisor_name,
                   s.nis as leader_nis, us.full_name as leader_name
            FROM extracurriculars e
            LEFT JOIN teachers t ON e.supervisor_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN students s ON e.student_leader_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            ORDER BY e.name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_extracurricular_by_id(extracurricular_id):
        query = """
            SELECT e.*, u.full_name as supervisor_name,
                   s.nis as leader_nis, us.full_name as leader_name
            FROM extracurriculars e
            LEFT JOIN teachers t ON e.supervisor_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN students s ON e.student_leader_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            WHERE e.extracurricular_id = %s
        """
        return execute_query(query, (extracurricular_id,), fetch_one=True)
    
    @staticmethod
    def create_extracurricular(name, description=None, supervisor_teacher_id=None,
                               student_leader_id=None, schedule_day=None, 
                               schedule_time=None, location=None, status='active'):
        query = """
            INSERT INTO extracurriculars (name, description, supervisor_teacher_id,
                                          student_leader_id, schedule_day, schedule_time, 
                                          location, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (name, description, supervisor_teacher_id,
                                     student_leader_id, schedule_day, schedule_time,
                                     location, status), commit=True)
    
    @staticmethod
    def update_extracurricular(extracurricular_id, name=None, description=None, 
                               supervisor_teacher_id=None, student_leader_id=None,
                               schedule_day=None, schedule_time=None, 
                               location=None, status=None):
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if supervisor_teacher_id is not None:
            updates.append("supervisor_teacher_id = %s")
            params.append(supervisor_teacher_id)
        if student_leader_id is not None:
            updates.append("student_leader_id = %s")
            params.append(student_leader_id)
        if schedule_day:
            updates.append("schedule_day = %s")
            params.append(schedule_day)
        if schedule_time:
            updates.append("schedule_time = %s")
            params.append(schedule_time)
        if location:
            updates.append("location = %s")
            params.append(location)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(extracurricular_id)
        query = f"UPDATE extracurriculars SET {', '.join(updates)} WHERE extracurricular_id = %s"
        execute_query(query, tuple(params), commit=True)
        return ExtracurricularModel.get_extracurricular_by_id(extracurricular_id)
    
    @staticmethod
    def delete_extracurricular(extracurricular_id):
        query = "DELETE FROM extracurriculars WHERE extracurricular_id = %s"
        execute_query(query, (extracurricular_id,), commit=True)
        return True
    
    @staticmethod
    def get_extracurriculars_for_dropdown():
        query = """
            SELECT extracurricular_id, name
            FROM extracurriculars
            WHERE status = 'active'
            ORDER BY name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_extracurricular_members(extracurricular_id):
        """Get all members of an extracurricular"""
        query = """
            SELECT s.*, u.full_name, u.photo, c.class_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            JOIN student_extracurriculars se ON s.student_id = se.student_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            WHERE se.extracurricular_id = %s AND s.status = 'active'
            ORDER BY u.full_name ASC
        """
        return execute_query(query, (extracurricular_id,))
    
    @staticmethod
    def add_student_to_extracurricular(student_id, extracurricular_id):
        query = """
            INSERT INTO student_extracurriculars (student_id, extracurricular_id)
            VALUES (%s, %s)
        """
        return execute_query(query, (student_id, extracurricular_id), commit=True)
    
    @staticmethod
    def remove_student_from_extracurricular(student_id, extracurricular_id):
        query = """
            DELETE FROM student_extracurriculars 
            WHERE student_id = %s AND extracurricular_id = %s
        """
        execute_query(query, (student_id, extracurricular_id), commit=True)
        return True
