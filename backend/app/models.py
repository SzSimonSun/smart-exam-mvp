# app/models.py - SQLAlchemy Models
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(120), nullable=False)
    role = Column(String(20), nullable=False)  # admin, teacher, student
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owned_classes = relationship("Class", back_populates="owner_teacher")
    class_memberships = relationship("ClassStudent", back_populates="student")
    created_questions = relationship("Question", back_populates="creator")
    created_papers = relationship("Paper", back_populates="creator")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    grade = Column(String(50))
    owner_teacher_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner_teacher = relationship("User", back_populates="owned_classes")
    students = relationship("ClassStudent", back_populates="class_")

class ClassStudent(Base):
    __tablename__ = "class_students"
    
    class_id = Column(Integer, ForeignKey("classes.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    class_ = relationship("Class", back_populates="students")
    student = relationship("User", back_populates="class_memberships")

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(80), nullable=False)
    module = Column(String(120))
    point = Column(String(200))
    subskill = Column(String(200))
    code = Column(String(120), unique=True)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"))
    level = Column(Integer)
    
    # Relationships
    parent = relationship("KnowledgePoint", remote_side=[id])
    questions = relationship("QuestionKnowledgeMap", back_populates="knowledge_point")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    stem = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)  # single, multiple, fill, judge, subjective
    difficulty = Column(Integer, default=2)  # 1-5
    options_json = Column(JSON)
    answer_json = Column(JSON)
    analysis = Column(Text)
    source_meta = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="draft")  # draft, reviewing, published
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_questions")
    knowledge_points = relationship("QuestionKnowledgeMap", back_populates="question")
    assets = relationship("QuestionAsset", back_populates="question")

class QuestionKnowledgeMap(Base):
    __tablename__ = "question_knowledge_map"
    
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    kp_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
    
    # Relationships
    question = relationship("Question", back_populates="knowledge_points")
    knowledge_point = relationship("KnowledgePoint", back_populates="questions")

class QuestionAsset(Base):
    __tablename__ = "question_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    file_uri = Column(Text, nullable=False)
    kind = Column(String(40))
    
    # Relationships
    question = relationship("Question", back_populates="assets")

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(80))
    grade = Column(String(50))
    layout_json = Column(JSON)
    qr_schema = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_papers")
    questions = relationship("PaperQuestion", back_populates="paper")
    versions = relationship("PaperVersion", back_populates="paper")

class PaperQuestion(Base):
    __tablename__ = "paper_questions"
    
    paper_id = Column(Integer, ForeignKey("papers.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)
    seq = Column(Integer, nullable=False)
    score = Column(Numeric(6, 2), default=0, nullable=False)
    section = Column(String(80))
    
    # Relationships
    paper = relationship("Paper", back_populates="questions")
    question = relationship("Question")

class PaperVersion(Base):
    __tablename__ = "paper_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    version_no = Column(Integer, nullable=False)
    pdf_uri = Column(Text, nullable=False)
    checksum = Column(String(128))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paper = relationship("Paper", back_populates="versions")

class AnswerSheet(Base):
    __tablename__ = "answer_sheets"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    qr_token = Column(String(120))
    upload_uri = Column(Text)
    status = Column(String(20), default="uploaded")  # uploaded, processed, graded, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    paper = relationship("Paper")
    student = relationship("User")
    class_ = relationship("Class")
    answers = relationship("Answer", back_populates="sheet")

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    sheet_id = Column(Integer, ForeignKey("answer_sheets.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    raw_omr = Column(JSON)
    raw_ocr = Column(JSON)
    parsed_json = Column(JSON)
    spent_ms = Column(Integer)
    is_objective = Column(Boolean, default=True)
    is_correct = Column(Boolean)
    score = Column(Numeric(6, 2))
    error_flag = Column(Boolean, default=False)
    
    # Relationships
    sheet = relationship("AnswerSheet", back_populates="answers")
    question = relationship("Question")

class StudentStat(Base):
    __tablename__ = "student_stats"
    
    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    kp_id = Column(Integer, ForeignKey("knowledge_points.id"), primary_key=True)
    total = Column(Integer, default=0)
    wrong = Column(Integer, default=0)
    last3_wrong_rate = Column(Numeric(5, 2))
    first_pass_rate = Column(Numeric(5, 2))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("User")
    knowledge_point = relationship("KnowledgePoint")

class IngestSession(Base):
    __tablename__ = "ingest_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    file_uri = Column(Text, nullable=False)
    status = Column(String(30), default="uploaded")  # uploaded, parsing, awaiting_review, partially_approved, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploader = relationship("User")
    items = relationship("IngestItem", back_populates="session")

class IngestItem(Base):
    __tablename__ = "ingest_items"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("ingest_sessions.id"))
    seq = Column(Integer)
    crop_uri = Column(Text)
    ocr_json = Column(JSON)
    candidate_type = Column(String(20))
    candidate_kps_json = Column(JSON)
    confidence = Column(Numeric(5, 2))
    review_status = Column(String(20), default="pending")  # pending, approved, rejected, edited
    approved_question_id = Column(Integer, ForeignKey("questions.id"))
    
    # Relationships
    session = relationship("IngestSession", back_populates="items")
    approved_question = relationship("Question")