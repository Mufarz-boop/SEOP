from app.database.db import execute_query

class StudentModel:
    @staticmethod
    def get_all_students():
        query = """
            SELECT s.*, u.full_name, u.register_number, u.username, u.photo,
                   c.class_name, c.grade_level, m.major_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN majors m ON s.major_id = m.major_id
            ORDER BY u.full_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_student_by_id(student_id):
        query = """
            SELECT s.*, u.full_name, u.register_number, u.username, u.photo,
                   c.class_name, c.grade_level, c.room_number, m.major_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN majors m ON s.major_id = m.major_id
            WHERE s.student_id = %s
        """
        return execute_query(query, (student_id,), fetch_one=True)
    
    @staticmethod
    def get_student_by_user_id(user_id):
        query = """
            SELECT s.*, u.full_name, u.register_number, u.username, u.photo,
                   c.class_name, c.grade_level, c.room_number, m.major_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN majors m ON s.major_id = m.major_id
            WHERE s.user_id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def get_students_by_class(class_id):
        query = """
            SELECT s.*, u.full_name, u.register_number, u.photo
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.class_id = %s AND s.status = 'active'
            ORDER BY u.full_name ASC
        """
        return execute_query(query, (class_id,))
    
    @staticmethod
    def create_student(user_id, nis, birth_date=None, gender=None, address=None,
                       phone_number=None, father_name=None, mother_name=None,
                       class_id=None, major_id=None, status='active'):
        query = """
            INSERT INTO students (user_id, nis, birth_date, gender, address, phone_number,
                                  father_name, mother_name, class_id, major_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (user_id, nis, birth_date, gender, address, phone_number,
                                     father_name, mother_name, class_id, major_id, status), commit=True)
    
    @staticmethod
    def update_student(student_id, nis=None, birth_date=None, gender=None, address=None,
                       phone_number=None, father_name=None, mother_name=None,
                       class_id=None, major_id=None, status=None):
        updates = []
        params = []
        
        if nis:
            updates.append("nis = %s")
            params.append(nis)
        if birth_date:
            updates.append("birth_date = %s")
            params.append(birth_date)
        if gender:
            updates.append("gender = %s")
            params.append(gender)
        if address:
            updates.append("address = %s")
            params.append(address)
        if phone_number:
            updates.append("phone_number = %s")
            params.append(phone_number)
        if father_name:
            updates.append("father_name = %s")
            params.append(father_name)
        if mother_name:
            updates.append("mother_name = %s")
            params.append(mother_name)
        if class_id is not None:
            updates.append("class_id = %s")
            params.append(class_id)
        if major_id is not None:
            updates.append("major_id = %s")
            params.append(major_id)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(student_id)
        query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = %s"
        execute_query(query, tuple(params), commit=True)
        return StudentModel.get_student_by_id(student_id)
    
    @staticmethod
    def delete_student(student_id):
        query = "DELETE FROM students WHERE student_id = %s"
        execute_query(query, (student_id,), commit=True)
        return True
    
    @staticmethod
    def get_students_for_dropdown():
        query = """
            SELECT s.student_id, u.full_name, s.nis, c.class_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            LEFT JOIN classes c ON s.class_id = c.class_id
            WHERE s.status = 'active'
            ORDER BY u.full_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_student_extracurriculars(student_id):
        """Get student's extracurricular activities"""
        query = """
            SELECT e.*, u.full_name as teacher_name
            FROM extracurriculars e
            JOIN student_extracurriculars se ON e.extracurricular_id = se.extracurricular_id
            LEFT JOIN teachers t ON e.supervisor_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE se.student_id = %s AND e.status = 'active'
        """
        return execute_query(query, (student_id,))
    
    @staticmethod
    def get_student_violations(student_id):
        """Get student's violation history"""
        query = """
            SELECT v.*, vt.name as violation_type_name
            FROM violations v
            JOIN violation_types vt ON v.violation_type_id = vt.id
            WHERE v.student_id = %s
            ORDER BY v.created_at DESC
        """
        return execute_query(query, (student_id,))
    
    @staticmethod
    def get_student_dashboard_stats(student_id):
        """Get statistics for student dashboard"""
        stats = {}
        
        # Get student info
        student = StudentModel.get_student_by_id(student_id)
        stats['student'] = student
        
        # Total reports made by this student
        user_id = student['user_id'] if student else None
        if user_id:
            query = "SELECT COUNT(*) as count FROM reports WHERE reporter_id = %s"
            stats['my_reports'] = execute_query(query, (user_id,), fetch_one=True)['count']
            
            # Total violations
            query = "SELECT COUNT(*) as count FROM violations WHERE student_id = %s"
            stats['my_violations'] = execute_query(query, (student_id,), fetch_one=True)['count']
            
            # Total violation points
            query = "SELECT COALESCE(SUM(points), 0) as total FROM violations WHERE student_id = %s"
            stats['violation_points'] = execute_query(query, (student_id,), fetch_one=True)['total']
        
        return stats