from typing import List, Optional
from dataclasses import dataclass
import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str

@dataclass
class Project:
    id: int
    title: str
    description: str
    deadline: str
    owner_id: int

@dataclass
class ChecklistItem:
    item: str
    done: bool

@dataclass
class Task:
    id: int
    project_id: int
    title: str
    checklist: List[ChecklistItem]
    comments: List[str]

@dataclass
class Consultation:
    id: int
    project_id: int
    dosen_name: str
    datetime: str
    topic: str

@dataclass
class TeamEvaluation:
    id: int
    project_id: int
    evaluator: str
    score: int
    comment: str

@dataclass
class Document:
    id: int
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime.datetime
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    uploaded_by: Optional[int] = None  # user_id