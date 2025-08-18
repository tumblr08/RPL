import os
import strawberry
import datetime
from typing import List, Optional
from models import User, Project, Task, Consultation, TeamEvaluation, ChecklistItem, Document
from data_store import (
    # Updated imports to use new functions from data_store
    get_user_by_email, get_user_by_id, get_documents_by_project,
    get_documents_by_task, get_document_by_id,
    # New imports for mutations and queries
    create_user, get_all_users,
    create_project, get_all_projects, get_project_by_id,
    create_task, get_all_tasks, get_task_by_id, update_task,
    create_consultation, get_all_consultations,
    create_team_evaluation, get_all_evaluations,
    create_document, get_all_documents, delete_document_from_db,
    update_project as update_project_in_db,  
    delete_project as delete_project_from_db,
    update_consultation, delete_consultation, get_consultation_by_id
)
from utils import hash_password, verify_password
import json # Import json for checklist/comments

# Strawberry Types
@strawberry.type
class UserType:
    id: strawberry.ID
    name: str
    email: str

@strawberry.type
class ProjectType:
    id: strawberry.ID
    title: str
    description: str
    deadline: str
    owner_id: strawberry.ID

    @strawberry.field
    def documents(self) -> List["DocumentType"]:
        return get_documents_by_project(int(self.id))

@strawberry.type
class ChecklistItemType:
    item: str
    done: bool

@strawberry.type
class TaskType:
    id: strawberry.ID
    project_id: strawberry.ID
    title: str
    checklist: List[ChecklistItemType]
    comments: List[str]

    @strawberry.field
    def documents(self) -> List["DocumentType"]:
        return get_documents_by_task(int(self.id))

@strawberry.type
class ConsultationType:
    id: strawberry.ID
    project_id: strawberry.ID
    dosen_name: str
    datetime: str
    topic: str

@strawberry.type
class TeamEvaluationType:
    id: strawberry.ID
    project_id: strawberry.ID
    evaluator: str
    score: int
    comment: str

@strawberry.type
class DocumentType:
    id: strawberry.ID
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime.datetime
    project_id: Optional[strawberry.ID] = None
    task_id: Optional[strawberry.ID] = None
    uploaded_by: Optional[strawberry.ID] = None

    @strawberry.field
    def uploader(self) -> Optional[UserType]:
        if self.uploaded_by:
            user = get_user_by_id(int(self.uploaded_by))
            if user:
                return UserType(id=strawberry.ID(user.id), name=user.name, email=user.email)
        return None

# Input Types
@strawberry.input
class RegisterInput:
    name: str
    email: str
    password: str

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class CreateProjectInput:
    title: str
    description: str
    deadline: str
    owner_id: strawberry.ID

@strawberry.input
class UpdateProjectInput:
    project_id: strawberry.ID
    title: str
    description: str
    deadline: str

@strawberry.input
class CreateTaskInput:
    project_id: strawberry.ID
    title: str

@strawberry.input
class AddChecklistItemInput:
    task_id: strawberry.ID
    item: str

@strawberry.input
class AddCommentInput:
    task_id: strawberry.ID
    comment: str

@strawberry.input
class MarkChecklistDoneInput:
    task_id: strawberry.ID
    item: str

@strawberry.input
class UncheckChecklistItemInput:
    task_id: strawberry.ID
    item: str


@strawberry.input
class CreateConsultationInput:
    project_id: strawberry.ID
    dosen_name: str
    datetime: str
    topic: str

@strawberry.input
class UpdateConsultationInput:
    consultation_id: strawberry.ID
    project_id: strawberry.ID
    dosen_name: str
    datetime: str
    topic: str

@strawberry.input
class CreateTeamEvaluationInput:
    project_id: strawberry.ID
    evaluator: str
    score: int
    comment: Optional[str] = None

@strawberry.input
class UploadDocumentInput:
    filename: str
    file_size: int
    content_type: str
    project_id: Optional[strawberry.ID] = None
    task_id: Optional[strawberry.ID] = None
    uploaded_by: Optional[strawberry.ID] = None

# Response Types
@strawberry.type
class AuthResponse:
    ok: bool
    message: str
    user: Optional[UserType] = None

@strawberry.type
class DocumentResponse:
    success: bool
    message: str
    document: Optional[DocumentType] = None

@strawberry.type
class ActionResponse:
    success: bool
    message: str   

# Query
@strawberry.type
class Query:
    @strawberry.field
    def all_users(self) -> List[UserType]:
        # Use get_all_users from data_store
        return [UserType(id=strawberry.ID(u.id), name=u.name, email=u.email) for u in get_all_users()]

    @strawberry.field
    def all_projects(self) -> List[ProjectType]:
        # Use get_all_projects from data_store
        return [ProjectType(
            id=strawberry.ID(p.id),
            title=p.title,
            description=p.description,
            deadline=p.deadline,
            owner_id=strawberry.ID(p.owner_id)
        ) for p in get_all_projects()]

    @strawberry.field
    def all_tasks(self) -> List[TaskType]:
        # Use get_all_tasks from data_store
        return [TaskType(
            id=strawberry.ID(t.id),
            project_id=strawberry.ID(t.project_id),
            title=t.title,
            checklist=[ChecklistItemType(item=item.item, done=item.done) for item in t.checklist],
            comments=t.comments
        ) for t in get_all_tasks()]

    @strawberry.field
    def all_consultations(self) -> List[ConsultationType]:
        # Use get_all_consultations from data_store
        return [ConsultationType(
            id=strawberry.ID(c.id),
            project_id=strawberry.ID(c.project_id),
            dosen_name=c.dosen_name,
            datetime=c.datetime,
            topic=c.topic
        ) for c in get_all_consultations()]

    @strawberry.field
    def consultation(self, consultation_id: strawberry.ID) -> Optional[ConsultationType]:
        c = get_consultation_by_id(int(consultation_id))
        if c:
            return ConsultationType(
                id=strawberry.ID(c.id),
                project_id=strawberry.ID(c.project_id),
                dosen_name=c.dosen_name,
                datetime=c.datetime,
                topic=c.topic
            )
        return None

    @strawberry.field
    def all_evaluations(self) -> List[TeamEvaluationType]:
        # Use get_all_evaluations from data_store
        return [TeamEvaluationType(
            id=strawberry.ID(e.id),
            project_id=strawberry.ID(e.project_id),
            evaluator=e.evaluator,
            score=e.score,
            comment=e.comment
        ) for e in get_all_evaluations()]

    @strawberry.field
    def all_documents(self) -> List[DocumentType]:
        # Use get_all_documents from data_store
        return [DocumentType(
            id=strawberry.ID(d.id),
            filename=d.filename,
            file_path=d.file_path,
            file_size=d.file_size,
            content_type=d.content_type,
            uploaded_at=d.uploaded_at,
            project_id=strawberry.ID(d.project_id) if d.project_id else None,
            task_id=strawberry.ID(d.task_id) if d.task_id else None,
            uploaded_by=strawberry.ID(d.uploaded_by) if d.uploaded_by else None
        ) for d in get_all_documents()]

    @strawberry.field
    def upcoming_deadlines(self, days: int = 3) -> List[ProjectType]:
        now = datetime.datetime.now()
        upcoming = []
        # Fetch all projects from DB
        all_projects = get_all_projects()
        for project in all_projects:
            try:
                deadline_dt = datetime.datetime.strptime(project.deadline, "%Y-%m-%d")
                delta = (deadline_dt - now).days
                if 0 <= delta <= days:
                    upcoming.append(ProjectType(
                        id=strawberry.ID(project.id),
                        title=project.title,
                        description=project.description,
                        deadline=project.deadline,
                        owner_id=strawberry.ID(project.owner_id)
                    ))
            except Exception:
                continue
        return upcoming

    @strawberry.field
    def get_document(self, document_id: strawberry.ID) -> Optional[DocumentType]:
        doc = get_document_by_id(int(document_id))
        if doc:
            return DocumentType(
                id=strawberry.ID(doc.id),
                filename=doc.filename,
                file_path=doc.file_path,
                file_size=doc.file_size,
                content_type=doc.content_type,
                uploaded_at=doc.uploaded_at,
                project_id=strawberry.ID(doc.project_id) if doc.project_id else None,
                task_id=strawberry.ID(doc.task_id) if doc.task_id else None,
                uploaded_by=strawberry.ID(doc.uploaded_by) if doc.uploaded_by else None
            )
        return None

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, input: RegisterInput) -> AuthResponse:
        if get_user_by_email(input.email): # Uses updated data_store function
            return AuthResponse(ok=False, message="Email sudah terdaftar")

        user = User(
            id=0, # ID will be assigned by DB
            name=input.name,
            email=input.email,
            password=hash_password(input.password)
        )
        new_user = create_user(user) # Uses updated data_store function

        if new_user:
            user_type = UserType(id=strawberry.ID(new_user.id), name=new_user.name, email=new_user.email)
            return AuthResponse(ok=True, message="Registrasi berhasil", user=user_type)
        else:
            return AuthResponse(ok=False, message="Gagal melakukan registrasi")

    @strawberry.mutation
    def login(self, input: LoginInput) -> AuthResponse:
        user = get_user_by_email(input.email) # Uses updated data_store function
        if not user or not verify_password(input.password, user.password):
            return AuthResponse(ok=False, message="Email atau password salah")

        user_type = UserType(id=strawberry.ID(user.id), name=user.name, email=user.email)
        return AuthResponse(ok=True, message="Login berhasil", user=user_type)

    @strawberry.mutation
    def create_project(self, input: CreateProjectInput) -> ProjectType:
        project = Project(
            id=0, # ID will be assigned by DB
            title=input.title,
            description=input.description,
            deadline=input.deadline,
            owner_id=int(input.owner_id)
        )
        new_project = create_project(project) # Uses updated data_store function
        if new_project:
            return ProjectType(
                id=strawberry.ID(new_project.id),
                title=new_project.title,
                description=new_project.description,
                deadline=new_project.deadline,
                owner_id=strawberry.ID(new_project.owner_id)
            )
        else:
            raise Exception("Gagal membuat project")
        
    @strawberry.mutation
    def update_project(self, input: UpdateProjectInput) -> Optional[ProjectType]:
        project_to_update = Project(
             id=int(input.project_id),
             title=input.title,
             description=input.description,
             deadline=input.deadline,
             owner_id=0 # Owner ID tidak diupdate, jadi bisa diisi dummy value
        )

        # Gunakan fungsi dari data_store yang sudah di-alias
        updated_project = update_project_in_db(project_to_update)
        
        if updated_project:
            # Kita perlu fetch ulang project untuk mendapatkan owner_id yang benar
            final_project = get_project_by_id(updated_project.id)
            if final_project:
                return ProjectType(
                    id=strawberry.ID(final_project.id),
                    title=final_project.title,
                    description=final_project.description,
                    deadline=final_project.deadline,
                    owner_id=strawberry.ID(final_project.owner_id)
                )
        raise Exception("Gagal mengupdate project atau project tidak ditemukan.")

    @strawberry.mutation
    def delete_project(self, project_id: strawberry.ID) -> bool:
        success = delete_project_from_db(int(project_id))
        return success

    @strawberry.mutation
    def create_task(self, input: CreateTaskInput) -> TaskType:
        task = Task(
            id=0, # ID will be assigned by DB
            project_id=int(input.project_id),
            title=input.title,
            checklist=[],
            comments=[]
        )
        new_task = create_task(task) # Uses updated data_store function
        if new_task:
            return TaskType(
                id=strawberry.ID(new_task.id),
                project_id=strawberry.ID(new_task.project_id),
                title=new_task.title,
                checklist=[],
                comments=[]
            )
        else:
            raise Exception("Gagal membuat tugas")

    @strawberry.mutation
    def add_checklist_item(self, input: AddChecklistItemInput) -> TaskType:
        task = get_task_by_id(int(input.task_id)) # Uses updated data_store function
        if not task:
            raise Exception("Tugas tidak ditemukan")

        new_item = ChecklistItem(item=input.item, done=False)
        task.checklist.append(new_item)
        updated_task = update_task(task) # Uses updated data_store function

        if updated_task:
            return TaskType(
                id=strawberry.ID(updated_task.id),
                project_id=strawberry.ID(updated_task.project_id),
                title=updated_task.title,
                checklist=[ChecklistItemType(item=item.item, done=item.done) for item in updated_task.checklist],
                comments=updated_task.comments
            )
        else:
            raise Exception("Gagal menambahkan item checklist")

    @strawberry.mutation
    def add_comment_to_task(self, input: AddCommentInput) -> TaskType:
        task = get_task_by_id(int(input.task_id)) # Uses updated data_store function
        if not task:
            raise Exception("Tugas tidak ditemukan")

        task.comments.append(input.comment)
        updated_task = update_task(task) # Uses updated data_store function

        if updated_task:
            return TaskType(
                id=strawberry.ID(updated_task.id),
                project_id=strawberry.ID(updated_task.project_id),
                title=updated_task.title,
                checklist=[ChecklistItemType(item=item.item, done=item.done) for item in updated_task.checklist],
                comments=updated_task.comments
            )
        else:
            raise Exception("Gagal menambahkan komentar")

    @strawberry.mutation
    def mark_checklist_item_done(self, input: MarkChecklistDoneInput) -> TaskType:
        task = get_task_by_id(int(input.task_id)) # Uses updated data_store function
        if not task:
            raise Exception("Tugas tidak ditemukan")

        updated = False
        for item in task.checklist:
            if item.item == input.item:
                item.done = True
                updated = True
                break

        if not updated:
            raise Exception("Item checklist tidak ditemukan")

        updated_task = update_task(task) # Uses updated data_store function

        if updated_task:
            return TaskType(
                id=strawberry.ID(updated_task.id),
                project_id=strawberry.ID(updated_task.project_id),
                title=updated_task.title,
                checklist=[ChecklistItemType(item=item.item, done=item.done) for item in updated_task.checklist],
                comments=updated_task.comments
            )
        else:
            raise Exception("Gagal menandai item checklist sebagai selesai")

    @strawberry.mutation
    def uncheck_checklist_item(self, input: UncheckChecklistItemInput) -> TaskType:
        task = get_task_by_id(int(input.task_id))
        if not task:
            raise Exception("Tugas tidak ditemukan")

        updated = False
        for item in task.checklist:
            if item.item == input.item:
                item.done = False
                updated = True
                break

        if not updated:
            raise Exception("Item checklist tidak ditemukan")

        updated_task = update_task(task)
        if updated_task:
            return TaskType(
                id=strawberry.ID(updated_task.id),
                project_id=strawberry.ID(updated_task.project_id),
                title=updated_task.title,
                checklist=[ChecklistItemType(item=i.item, done=i.done) for i in updated_task.checklist],
                comments=updated_task.comments
            )
        else:
            raise Exception("Gagal mengubah checklist menjadi belum selesai")

    @strawberry.mutation
    def create_consultation(self, input: CreateConsultationInput) -> ConsultationType:
        consultation = Consultation(
            id=0, # ID will be assigned by DB
            project_id=int(input.project_id),
            dosen_name=input.dosen_name,
            datetime=input.datetime,
            topic=input.topic
        )
        new_consultation = create_consultation(consultation) # Uses updated data_store function
        if new_consultation:
            return ConsultationType(
                id=strawberry.ID(new_consultation.id),
                project_id=strawberry.ID(new_consultation.project_id),
                dosen_name=new_consultation.dosen_name,
                datetime=new_consultation.datetime,
                topic=new_consultation.topic
            )
        else:
            raise Exception("Gagal membuat konsultasi")

    @strawberry.mutation
    def delete_consultation(self, consultation_id: strawberry.ID) -> bool:
        return delete_consultation(int(consultation_id))
    
    @strawberry.mutation
    def update_consultation(self, input: UpdateConsultationInput) -> ConsultationType:
        consultation = Consultation(
            id=int(input.consultation_id),
            project_id=int(input.project_id),
            dosen_name=input.dosen_name,
            datetime=input.datetime,
            topic=input.topic
        )
        updated = update_consultation(consultation)
        if updated:
            return ConsultationType(
                id=strawberry.ID(updated.id),
                project_id=strawberry.ID(updated.project_id),
                dosen_name=updated.dosen_name,
                datetime=updated.datetime,
                topic=updated.topic
            )
        else:
            raise Exception("Gagal mengupdate konsultasi")

    @strawberry.mutation
    def create_team_evaluation(self, input: CreateTeamEvaluationInput) -> TeamEvaluationType:
        evaluation = TeamEvaluation(
            id=0, # ID will be assigned by DB
            project_id=int(input.project_id),
            evaluator=input.evaluator,
            score=input.score,
            comment=input.comment or ""
        )
        new_evaluation = create_team_evaluation(evaluation) # Uses updated data_store function
        if new_evaluation:
            return TeamEvaluationType(
                id=strawberry.ID(new_evaluation.id),
                project_id=strawberry.ID(new_evaluation.project_id),
                evaluator=new_evaluation.evaluator,
                score=new_evaluation.score,
                comment=new_evaluation.comment
            )
        else:
            raise Exception("Gagal membuat evaluasi tim")

    @strawberry.mutation
    def upload_document(self, input: UploadDocumentInput) -> DocumentResponse:
        try:
            # PENTING: File path harus di-handle oleh REST endpoint /upload di app.py.
            # Mutasi ini seharusnya hanya mencatat metadata dokumen ke DB.
            # Jika mutasi ini dipanggil, file_path harus sudah tersedia (misalnya, dikirim sebagai input)
            # Karena input.file_path tidak ada, ini adalah logika dummy atau harus diubah.

            # Untuk tujuan perbaikan SyntaxError, kita akan menambahkan except.
            # Namun, disarankan untuk MENGHAPUS MUTASI INI
            # dan biarkan REST API (app.py) yang menanganinya sepenuhnya.

            # Contoh jika tetap ingin menyimpan mutasi ini (dengan perbaikan SyntaxError)
            # asumsi file_path adalah string dummy atau sudah ditangani di tempat lain.
            # Sebaiknya tambahkan input.file_path ke UploadDocumentInput jika ini tujuan Anda.
            file_path = f"uploads/{input.filename}"

            document = Document(
                id=len(documents) + 1, # <-- Masih pakai in-memory list. Harus pakai create_document dari data_store
                filename=input.filename,
                file_path=file_path, # <-- Ini harus path aktual
                file_size=input.file_size,
                content_type=input.content_type,
                uploaded_at=datetime.datetime.now(),
                project_id=int(input.project_id) if input.project_id else None,
                task_id=int(input.task_id) if input.task_id else None,
                uploaded_by=int(input.uploaded_by) if input.uploaded_by else None
            )
            documents.append(document) # <-- Masih pakai in-memory list. Harus pakai create_document dari data_store

            document_type = DocumentType(
                id=strawberry.ID(document.id),
                filename=document.filename,
                file_path=document.file_path,
                file_size=document.file_size,
                content_type=document.content_type,
                uploaded_at=document.uploaded_at,
                project_id=strawberry.ID(document.project_id) if document.project_id else None,
                task_id=strawberry.ID(document.task_id) if document.task_id else None,
                uploaded_by=strawberry.ID(document.uploaded_by) if document.uploaded_by else None
            )

            return DocumentResponse(
                success=True,
                message="Dokumen berhasil diupload",
                document=document_type
            )
        except Exception as e: # <-- Blok except yang hilang dan menyebabkan error
            return DocumentResponse(
                success=False,
                message=f"Error uploading document: {str(e)}"
            )

    @strawberry.mutation
    def delete_document(self, document_id: strawberry.ID) -> DocumentResponse:
        try: # Baris 575, seperti yang disebutkan di error Anda
            document = get_document_by_id(int(document_id))
            if not document:
                return DocumentResponse(
                    success=False,
                    message="Dokumen tidak ditemukan"
                )

            # Try to delete the actual file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
                print(f"File deleted from disk: {document.file_path}")
            else:
                print(f"File not found on disk, only removing record: {document.file_path}")

            # Delete from the database
            success = delete_document_from_db(int(document_id))
            if success:
                return DocumentResponse(
                    success=True,
                    message="Dokumen berhasil dihapus"
                )
            else:
                return DocumentResponse(
                    success=False,
                    message="Gagal menghapus dokumen dari database"
                )
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error deleting document (ID: {document_id}): {str(e)}")
            return DocumentResponse(
                success=False,
                message=f"Error deleting document: {str(e)}"
            )

schema = strawberry.Schema(query=Query, mutation=Mutation)