from app.database.db import execute_query

class TeacherModel:
    @staticmethod
    def get_all_teachers():
        query = """
            SELECT t.*, u.full_name, u.register_number, u.username, u.photo, 
                   s.subject_name, s.subject_id
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            LEFT JOIN subjects s ON t.subject_id = s.subject_id
            ORDER BY u.full_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_teacher_by_id(teacher_id):
        query = """
            SELECT t.*, u.full_name, u.register_number, u.username, u.photo,
                   s.subject_name, s.subject_id
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            LEFT JOIN subjects s ON t.subject_id = s.subject_id
            WHERE t.teacher_id = %s
        """
        return execute_query(query, (teacher_id,), fetch_one=True)
    
    @staticmethod
    def get_teacher_by_user_id(user_id):
        query = """
            SELECT t.*, u.full_name, u.register_number, u.username, u.photo,
                   s.subject_name, s.subject_id
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            LEFT JOIN subjects s ON t.subject_id = s.subject_id
            WHERE t.user_id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def create_teacher(user_id, nip=None, gender=None, birth_date=None, phone_number=None,
                       address=None, department='Akademik', subject_id=None, 
                       join_date=None, status='active'):
        query = """
            INSERT INTO teachers (user_id, nip, gender, birth_date, phone_number, 
                                  address, department, subject_id, join_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (user_id, nip, gender, birth_date, phone_number,
                                     address, department, subject_id, join_date, status), commit=True)
    
    @staticmethod
    def update_teacher(teacher_id, nip=None, gender=None, birth_date=None, phone_number=None,
                       address=None, department=None, subject_id=None, status=None):
        updates = []
        params = []
        
        if nip:
            updates.append("nip = %s")
            params.append(nip)
        if gender:
            updates.append("gender = %s")
            params.append(gender)
        if birth_date:
            updates.append("birth_date = %s")
            params.append(birth_date)
        if phone_number:
            updates.append("phone_number = %s")
            params.append(phone_number)
        if address:
            updates.append("address = %s")
            params.append(address)
        if department:
            updates.append("department = %s")
            params.append(department)
        if subject_id is not None:
            updates.append("subject_id = %s")
            params.append(subject_id)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(teacher_id)
        query = f"UPDATE teachers SET {', '.join(updates)} WHERE teacher_id = %s"
        execute_query(query, tuple(params), commit=True)
        return TeacherModel.get_teacher_by_id(teacher_id)
    
    @staticmethod
    def delete_teacher(teacher_id):
        query = "DELETE FROM teachers WHERE teacher_id = %s"
        execute_query(query, (teacher_id,), commit=True)
        return True
    
    @staticmethod
    def get_teachers_for_dropdown():
        query = """
            SELECT t.teacher_id, u.full_name, t.nip
            FROM teachers t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.status = 'active'
            ORDER BY u.full_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_homeroom_classes(teacher_id):
        """Get classes where teacher is homeroom teacher"""
        query = """
            SELECT c.*, m.major_name,
                   (SELECT COUNT(*) FROM students WHERE class_id = c.class_id) as student_count
            FROM classes c
            LEFT JOIN majors m ON c.major_id = m.major_id
            WHERE c.homeroom_teacher_id = %s
            ORDER BY c.class_name ASC
        """
        return execute_query(query, (teacher_id,))
    
    @staticmethod
    def get_teacher_dashboard_stats(teacher_id):
        """Get statistics for teacher dashboard"""
        stats = {}
        
        # Get homeroom classes
        homeroom_classes = TeacherModel.get_homeroom_classes(teacher_id)
        stats['homeroom_classes'] = homeroom_classes
        stats['total_homeroom_classes'] = len(homeroom_classes)
        
        # Total students in homeroom classes
        total_students = 0
        for cls in homeroom_classes:
            total_students += cls['student_count']
        stats['total_students'] = total_students
        
        # Reports made by this teacher
        query = """
            SELECT COUNT(*) as count FROM reports 
            WHERE reporter_id = (SELECT user_id FROM teachers WHERE teacher_id = %s)
        """
        stats['my_reports'] = execute_query(query, (teacher_id,), fetch_one=True)['count']
        
        return stats
