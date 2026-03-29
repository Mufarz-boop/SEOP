from app.database.db import execute_query

class ClassModel:
    @staticmethod
    def get_all_classes():
        query = """
            SELECT c.*, m.major_name, 
                   u.full_name as homeroom_teacher_name,
                   (SELECT COUNT(*) FROM students WHERE class_id = c.class_id AND status = 'active') as student_count
            FROM classes c
            LEFT JOIN majors m ON c.major_id = m.major_id
            LEFT JOIN teachers t ON c.homeroom_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            ORDER BY c.grade_level ASC, c.class_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_class_by_id(class_id):
        query = """
            SELECT c.*, m.major_name, 
                   u.full_name as homeroom_teacher_name
            FROM classes c
            LEFT JOIN majors m ON c.major_id = m.major_id
            LEFT JOIN teachers t ON c.homeroom_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE c.class_id = %s
        """
        return execute_query(query, (class_id,), fetch_one=True)
    
    @staticmethod
    def create_class(class_name, grade_level, major_id=None, academic_year='2025/2026',
                     capacity=30, room_number=None, homeroom_teacher_id=None, status='active'):
        query = """
            INSERT INTO classes (class_name, grade_level, major_id, academic_year, 
                                capacity, room_number, homeroom_teacher_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (class_name, grade_level, major_id, academic_year,
                                     capacity, room_number, homeroom_teacher_id, status), commit=True)
    
    @staticmethod
    def update_class(class_id, class_name=None, grade_level=None, major_id=None,
                     academic_year=None, capacity=None, room_number=None, 
                     homeroom_teacher_id=None, status=None):
        updates = []
        params = []
        
        if class_name:
            updates.append("class_name = %s")
            params.append(class_name)
        if grade_level:
            updates.append("grade_level = %s")
            params.append(grade_level)
        if major_id is not None:
            updates.append("major_id = %s")
            params.append(major_id)
        if academic_year:
            updates.append("academic_year = %s")
            params.append(academic_year)
        if capacity:
            updates.append("capacity = %s")
            params.append(capacity)
        if room_number:
            updates.append("room_number = %s")
            params.append(room_number)
        if homeroom_teacher_id is not None:
            updates.append("homeroom_teacher_id = %s")
            params.append(homeroom_teacher_id)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(class_id)
        query = f"UPDATE classes SET {', '.join(updates)} WHERE class_id = %s"
        execute_query(query, tuple(params), commit=True)
        return ClassModel.get_class_by_id(class_id)
    
    @staticmethod
    def delete_class(class_id):
        query = "DELETE FROM classes WHERE class_id = %s"
        execute_query(query, (class_id,), commit=True)
        return True
    
    @staticmethod
    def get_classes_for_dropdown():
        query = """
            SELECT class_id, class_name, grade_level
            FROM classes
            WHERE status = 'active'
            ORDER BY grade_level ASC, class_name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_classes_by_grade(grade_level):
        query = """
            SELECT c.*, m.major_name
            FROM classes c
            LEFT JOIN majors m ON c.major_id = m.major_id
            WHERE c.grade_level = %s AND c.status = 'active'
            ORDER BY c.class_name ASC
        """
        return execute_query(query, (grade_level,))
