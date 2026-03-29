from app.database.db import execute_query

class OrganizationModel:
    @staticmethod
    def get_all_organizations():
        query = """
            SELECT o.*, u.full_name as supervisor_name,
                   s.nis as president_nis, us.full_name as president_name
            FROM school_organizations o
            LEFT JOIN teachers t ON o.supervisor_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN students s ON o.president_student_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            ORDER BY o.name ASC
        """
        return execute_query(query)
    
    @staticmethod
    def get_organization_by_id(organization_id):
        query = """
            SELECT o.*, u.full_name as supervisor_name,
                   s.nis as president_nis, us.full_name as president_name
            FROM school_organizations o
            LEFT JOIN teachers t ON o.supervisor_teacher_id = t.teacher_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN students s ON o.president_student_id = s.student_id
            LEFT JOIN users us ON s.user_id = us.user_id
            WHERE o.organization_id = %s
        """
        return execute_query(query, (organization_id,), fetch_one=True)
    
    @staticmethod
    def create_organization(name, description=None, supervisor_teacher_id=None,
                           president_student_id=None, meeting_day=None,
                           meeting_time=None, location=None, status='active'):
        query = """
            INSERT INTO school_organizations (name, description, supervisor_teacher_id,
                                              president_student_id, meeting_day, 
                                              meeting_time, location, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (name, description, supervisor_teacher_id,
                                     president_student_id, meeting_day, meeting_time,
                                     location, status), commit=True)
    
    @staticmethod
    def update_organization(organization_id, name=None, description=None,
                           supervisor_teacher_id=None, president_student_id=None,
                           meeting_day=None, meeting_time=None, 
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
        if president_student_id is not None:
            updates.append("president_student_id = %s")
            params.append(president_student_id)
        if meeting_day:
            updates.append("meeting_day = %s")
            params.append(meeting_day)
        if meeting_time:
            updates.append("meeting_time = %s")
            params.append(meeting_time)
        if location:
            updates.append("location = %s")
            params.append(location)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return None
        
        params.append(organization_id)
        query = f"UPDATE school_organizations SET {', '.join(updates)} WHERE organization_id = %s"
        execute_query(query, tuple(params), commit=True)
        return OrganizationModel.get_organization_by_id(organization_id)
    
    @staticmethod
    def delete_organization(organization_id):
        query = "DELETE FROM school_organizations WHERE organization_id = %s"
        execute_query(query, (organization_id,), commit=True)
        return True
    
    @staticmethod
    def get_organizations_for_dropdown():
        query = """
            SELECT organization_id, name
            FROM school_organizations
            WHERE status = 'active'
            ORDER BY name ASC
        """
        return execute_query(query)
