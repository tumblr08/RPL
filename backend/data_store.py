import os
import mysql.connector
from mysql.connector import Error
import json
from typing import Optional, List
from models import User, Project, Task, Consultation, TeamEvaluation, Document, ChecklistItem
import datetime

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST') or os.getenv('DB_HOST') or 'mysql.railway.internal',
    'database': os.getenv('MYSQL_DATABASE') or os.getenv('DB_NAME') or 'railway',
    'user': os.getenv('MYSQL_USER') or os.getenv('DB_USER') or 'root',
    'password': os.getenv('MYSQL_PASSWORD') or os.getenv('DB_PASS'),
    'port': int(os.getenv('MYSQL_PORT', os.getenv('DB_PORT', '3306')))
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# --- User Operations ---

def get_user_by_email(email: str) -> Optional[User]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()
        if user_data:
            return User(**user_data)
        return None
    except Error as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_user_by_id(user_id: int) -> Optional[User]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(**user_data)
        return None
    except Error as e:
        print(f"Error fetching user by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def create_user(user: User) -> Optional[User]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.name, user.email, user.password))
        conn.commit()
        user.id = cursor.lastrowid # Set the ID from the auto-increment
        return user
    except Error as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_users() -> List[User]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users"
        cursor.execute(query)
        users_data = cursor.fetchall()
        return [User(**u) for u in users_data]
    except Error as e:
        print(f"Error fetching all users: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Project Operations ---

def create_project(project: Project) -> Optional[Project]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO projects (title, description, deadline, owner_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (project.title, project.description, project.deadline, project.owner_id))
        conn.commit()
        project.id = cursor.lastrowid
        return project
    except Error as e:
        print(f"Error creating project: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_projects() -> List[Project]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM projects"
        cursor.execute(query)
        projects_data = cursor.fetchall()
        return [Project(**p) for p in projects_data]
    except Error as e:
        print(f"Error fetching all projects: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_project_by_id(project_id: int) -> Optional[Project]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM projects WHERE id = %s"
        cursor.execute(query, (project_id,))
        project_data = cursor.fetchone()
        if project_data:
            return Project(**project_data)
        return None
    except Error as e:
        print(f"Error fetching project by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_project(project: Project) -> Optional[Project]:
    """Mengupdate project yang ada di database."""
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = "UPDATE projects SET title = %s, description = %s, deadline = %s WHERE id = %s"
        cursor.execute(query, (project.title, project.description, project.deadline, project.id))
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return project
    except Error as e:
        print(f"Error updating project: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_project(project_id: int) -> bool:
    """Menghapus project dari database berdasarkan ID."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Hapus juga semua yang terkait dengan project ini (cascade delete)
        # Contoh: Hapus tasks, documents, dll. Ini penting untuk integritas data.
        cursor.execute("DELETE FROM tasks WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM documents WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM consultations WHERE project_id = %s", (project_id,))
        cursor.execute("DELETE FROM team_evaluations WHERE project_id = %s", (project_id,))
        
        # Terakhir, hapus project itu sendiri
        query = "DELETE FROM projects WHERE id = %s"
        cursor.execute(query, (project_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting project and related data: {e}")
        conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Task Operations ---

def create_task(task: Task) -> Optional[Task]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        # Store checklist and comments as JSON strings
        checklist_json = json.dumps([item.__dict__ for item in task.checklist])
        comments_json = json.dumps(task.comments)
        query = "INSERT INTO tasks (project_id, title, checklist, comments) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (task.project_id, task.title, checklist_json, comments_json))
        conn.commit()
        task.id = cursor.lastrowid
        return task
    except Error as e:
        print(f"Error creating task: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_tasks() -> List[Task]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM tasks"
        cursor.execute(query)
        tasks_data = cursor.fetchall()
        # Deserialize JSON fields
        for t in tasks_data:
            t['checklist'] = [ChecklistItem(**item) for item in json.loads(t['checklist'])] if t['checklist'] else []
            t['comments'] = json.loads(t['comments']) if t['comments'] else []
        return [Task(**t) for t in tasks_data]
    except Error as e:
        print(f"Error fetching all tasks: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_task_by_id(task_id: int) -> Optional[Task]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        task_data = cursor.fetchone()
        if task_data:
            task_data['checklist'] = [ChecklistItem(**item) for item in json.loads(task_data['checklist'])] if task_data['checklist'] else []
            task_data['comments'] = json.loads(task_data['comments']) if task_data['comments'] else []
            return Task(**task_data)
        return None
    except Error as e:
        print(f"Error fetching task by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_task(task: Task) -> Optional[Task]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        checklist_json = json.dumps([item.__dict__ for item in task.checklist])
        comments_json = json.dumps(task.comments)
        query = "UPDATE tasks SET title = %s, checklist = %s, comments = %s WHERE id = %s"
        cursor.execute(query, (task.title, checklist_json, comments_json, task.id))
        conn.commit()
        return task
    except Error as e:
        print(f"Error updating task: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Consultation Operations ---

def get_consultation_by_id(consultation_id: int) -> Optional[Consultation]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM consultations WHERE id = %s"
        cursor.execute(query, (consultation_id,))
        data = cursor.fetchone()
        if data:
            return Consultation(**data)
        return None
    except Error as e:
        print(f"Error fetching consultation by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def update_consultation(consultation: Consultation) -> Optional[Consultation]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = """
            UPDATE consultations
            SET project_id = %s, dosen_name = %s, datetime = %s, topic = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            consultation.project_id,
            consultation.dosen_name,
            consultation.datetime,
            consultation.topic,
            consultation.id
        ))
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return consultation
    except Error as e:
        print(f"Error updating consultation: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_consultation(consultation_id: int) -> bool:
    """Menghapus consultation dari database berdasarkan ID."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        query = "DELETE FROM consultations WHERE id = %s"
        cursor.execute(query, (consultation_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting consultation: {e}")
        conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def create_consultation(consultation: Consultation) -> Optional[Consultation]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO consultations (project_id, dosen_name, datetime, topic) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (consultation.project_id, consultation.dosen_name, consultation.datetime, consultation.topic))
        conn.commit()
        consultation.id = cursor.lastrowid
        return consultation
    except Error as e:
        print(f"Error creating consultation: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_consultations() -> List[Consultation]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM consultations"
        cursor.execute(query)
        consultations_data = cursor.fetchall()
        return [Consultation(**c) for c in consultations_data]
    except Error as e:
        print(f"Error fetching all consultations: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Team Evaluation Operations ---

def create_team_evaluation(evaluation: TeamEvaluation) -> Optional[TeamEvaluation]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO team_evaluations (project_id, evaluator, score, comment) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (evaluation.project_id, evaluation.evaluator, evaluation.score, evaluation.comment))
        conn.commit()
        evaluation.id = cursor.lastrowid
        return evaluation
    except Error as e:
        print(f"Error creating team evaluation: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_evaluations() -> List[TeamEvaluation]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM team_evaluations"
        cursor.execute(query)
        evaluations_data = cursor.fetchall()
        return [TeamEvaluation(**e) for e in evaluations_data]
    except Error as e:
        print(f"Error fetching all evaluations: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- Document Operations ---

def create_document(document: Document) -> Optional[Document]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO documents 
            (filename, file_path, file_size, content_type, uploaded_at, project_id, task_id, uploaded_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            document.filename, document.file_path, document.file_size, document.content_type, 
            document.uploaded_at, document.project_id, document.task_id, document.uploaded_by
        ))
        conn.commit()
        document.id = cursor.lastrowid
        return document
    except Error as e:
        print(f"Error creating document: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_documents() -> List[Document]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM documents"
        cursor.execute(query)
        documents_data = cursor.fetchall()
        
        # Convert 'uploaded_at' string to datetime object if it's a string
        for doc in documents_data:
            if isinstance(doc['uploaded_at'], str):
                try:
                    doc['uploaded_at'] = datetime.datetime.fromisoformat(doc['uploaded_at'])
                except ValueError:
                    # Handle cases where the string might not be in a perfect isoformat
                    # You might need to adjust the format string if it's different
                    doc['uploaded_at'] = datetime.datetime.strptime(doc['uploaded_at'], "%Y-%m-%d %H:%M:%S") 
            # If it's already a datetime object, do nothing (as per models.py)
        return [Document(**d) for d in documents_data]
    except Error as e:
        print(f"Error fetching all documents: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_documents_by_project(project_id: int) -> List[Document]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM documents WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        documents_data = cursor.fetchall()
        for doc in documents_data:
            if isinstance(doc['uploaded_at'], str):
                try:
                    doc['uploaded_at'] = datetime.datetime.fromisoformat(doc['uploaded_at'])
                except ValueError:
                    doc['uploaded_at'] = datetime.datetime.strptime(doc['uploaded_at'], "%Y-%m-%d %H:%M:%S")
        return [Document(**d) for d in documents_data]
    except Error as e:
        print(f"Error fetching documents by project: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_documents_by_task(task_id: int) -> List[Document]:
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM documents WHERE task_id = %s"
        cursor.execute(query, (task_id,))
        documents_data = cursor.fetchall()
        for doc in documents_data:
            if isinstance(doc['uploaded_at'], str):
                try:
                    doc['uploaded_at'] = datetime.datetime.fromisoformat(doc['uploaded_at'])
                except ValueError:
                    doc['uploaded_at'] = datetime.datetime.strptime(doc['uploaded_at'], "%Y-%m-%d %H:%M:%S")
        return [Document(**d) for d in documents_data]
    except Error as e:
        print(f"Error fetching documents by task: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_document_by_id(doc_id: int) -> Optional[Document]:
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM documents WHERE id = %s"
        cursor.execute(query, (doc_id,))
        document_data = cursor.fetchone()
        if document_data:
            if isinstance(document_data['uploaded_at'], str):
                try:
                    document_data['uploaded_at'] = datetime.datetime.fromisoformat(document_data['uploaded_at'])
                except ValueError:
                    document_data['uploaded_at'] = datetime.datetime.strptime(document_data['uploaded_at'], "%Y-%m-%d %H:%M:%S")
            return Document(**document_data)
        return None
    except Error as e:
        print(f"Error fetching document by ID: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_document_from_db(document_id: int) -> bool:
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        query = "DELETE FROM documents WHERE id = %s"
        cursor.execute(query, (document_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting document from DB: {e}")
        conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()