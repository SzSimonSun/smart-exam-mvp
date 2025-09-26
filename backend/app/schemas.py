# app/schemas.py - Pydantic Models for API Request/Response
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from decimal import Decimal

# Base Schema
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseSchema):
    email: EmailStr
    name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

class CurrentUser(UserResponse):
    pass

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Class Schemas
class ClassBase(BaseSchema):
    name: str
    grade: Optional[str] = None

class ClassCreate(ClassBase):
    student_ids: List[int] = Field(default_factory=list)

class ClassResponse(ClassBase):
    id: int
    owner_teacher_id: int

class ClassWithStudents(ClassResponse):
    students: List[UserResponse] = Field(default_factory=list)

# Knowledge Point Schemas
class KnowledgePointBase(BaseSchema):
    subject: str
    module: Optional[str] = None
    point: Optional[str] = None
    subskill: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None

class KnowledgePointCreate(KnowledgePointBase):
    parent_id: Optional[int] = None

class KnowledgePointResponse(KnowledgePointBase):
    id: int
    parent_id: Optional[int] = None
    children: List['KnowledgePointResponse'] = Field(default_factory=list)

# Question Schemas
class QuestionBase(BaseSchema):
    stem: str
    type: str  # single, multiple, fill, judge, subjective
    difficulty: int = 2
    options_json: Optional[Dict[str, Any]] = None
    answer_json: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    source_meta: Optional[Dict[str, Any]] = None

class QuestionCreate(QuestionBase):
    knowledge_point_ids: List[int] = Field(default_factory=list)

class QuestionUpdate(BaseModel):
    stem: Optional[str] = None
    type: Optional[str] = None
    difficulty: Optional[int] = None
    options_json: Optional[Dict[str, Any]] = None
    answer_json: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    knowledge_point_ids: Optional[List[int]] = None

class QuestionResponse(QuestionBase):
    id: int
    created_by: int
    status: str
    created_at: datetime
    knowledge_points: List[KnowledgePointResponse] = Field(default_factory=list)

class QuestionListResponse(BaseModel):
    items: List[QuestionResponse]
    total: int
    page: int
    size: int

# Paper Schemas
class PaperQuestionItem(BaseModel):
    question_id: int
    seq: int
    score: Decimal
    section: Optional[str] = None

class PaperBase(BaseSchema):
    name: str
    subject: Optional[str] = None
    grade: Optional[str] = None
    layout_json: Optional[Dict[str, Any]] = None

class PaperCreate(PaperBase):
    questions: List[PaperQuestionItem]

class PaperResponse(PaperBase):
    id: int
    created_by: int
    created_at: datetime
    qr_schema: Optional[Dict[str, Any]] = None

class PaperExportResponse(BaseModel):
    pdf_uri: str
    qr_schema: Dict[str, Any]

# Answer Sheet Schemas
class AnswerSheetUpload(BaseModel):
    paper_id: int
    class_id: int
    student_id: Optional[int] = None


class AnswerSheetResponse(BaseModel):
    id: int
    paper_id: int
    student_id: Optional[int] = None
    class_id: int
    status: str
    created_at: datetime

class AnswerResponse(BaseModel):
    id: int
    question_id: int
    parsed_json: Optional[Dict[str, Any]] = None
    is_objective: bool
    is_correct: Optional[bool] = None
    score: Optional[Decimal] = None
    error_flag: bool = False

class AnswerSheetReport(BaseModel):
    sheet_id: int
    student_name: str
    paper_name: str
    total_score: Decimal
    answers: List[AnswerResponse] = Field(default_factory=list)

# Statistics Schemas
class KnowledgePointStat(BaseModel):
    kp_id: int
    kp_name: str
    total: int
    wrong: int
    wrong_rate: float
    last3_wrong_rate: Optional[float] = None


class StudentKnowledgeStats(BaseModel):
    student_id: int
    student_name: str
    knowledge_points: List[KnowledgePointStat] = Field(default_factory=list)


class ClassOverview(BaseModel):
    class_id: int
    class_name: str
    student_count: int
    avg_score: float
    top_wrong_kps: List[KnowledgePointStat] = Field(default_factory=list)

# Ingest Schemas
class IngestSessionCreate(BaseModel):
    pass  # File will be uploaded separately

class IngestSessionResponse(BaseModel):
    id: int
    uploader_id: int
    file_uri: str
    status: str
    created_at: datetime

class IngestItemResponse(BaseModel):
    id: int
    session_id: int
    seq: Optional[int] = None
    crop_uri: Optional[str] = None
    ocr_json: Optional[Dict[str, Any]] = None
    candidate_type: Optional[str] = None
    candidate_kps_json: Optional[Dict[str, Any]] = None
    confidence: Optional[Decimal] = None
    review_status: str

class IngestItemApprove(BaseModel):
    stem: Optional[str] = None
    type: Optional[str] = None
    difficulty: Optional[int] = None
    options_json: Optional[Dict[str, Any]] = None
    answer_json: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    knowledge_point_ids: List[int] = Field(default_factory=list)

class IngestItemReject(BaseModel):
    reason: str

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None

# Update forward references
KnowledgePointResponse.model_rebuild()