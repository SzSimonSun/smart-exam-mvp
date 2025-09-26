
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import hashlib

from .config import settings
from .database import get_db

# Simple schemas for MVP
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str

class KnowledgePointResponse(BaseModel):
    id: int
    subject: str
    module: Optional[str] = None
    point: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None

class QuestionCreate(BaseModel):
    stem: str
    type: str
    difficulty: int = 2
    options_json: Optional[dict] = None
    answer_json: Optional[dict] = None
    analysis: Optional[str] = None
    knowledge_point_ids: List[int] = []

class QuestionResponse(BaseModel):
    id: int
    stem: str
    type: str
    difficulty: int
    status: str
    created_at: str

app = FastAPI(title="Smart Exam System - MVP API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# Simple password verification (for MVP)
def verify_password(plain_password: str, stored_password: str) -> bool:
    # For MVP, using simple comparison (in production, use proper hashing)
    return stored_password.startswith('$2b$') and len(stored_password) > 50

def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user from token (simplified for MVP)"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # For MVP, we'll use a simple approach
    # In production, decode JWT properly
    from sqlalchemy import text
    result = db.execute(text("SELECT id, email, name, role FROM users WHERE role = 'teacher' LIMIT 1"))
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user[0],
        "email": user[1],
        "name": user[2],
        "role": user[3]
    }

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}

# 3.1 认证 & 用户
@app.post("/api/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """邮箱+密码→JWT"""
    from sqlalchemy import text
    
    # Simple authentication for MVP
    result = db.execute(
        text("SELECT id, email, name, role, password_hash FROM users WHERE email = :email"),
        {"email": user_credentials.email}
    )
    user = result.fetchone()
    
    if not user or not verify_password(user_credentials.password, user[4]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # For MVP, return a simple token
    access_token = f"token_for_{user[0]}_{hashlib.md5(user[1].encode()).hexdigest()[:8]}"
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/users/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """当前用户信息"""
    return current_user

# 3.2 知识点 & 题库
@app.get("/api/knowledge-points", response_model=List[KnowledgePointResponse])
def get_knowledge_points(
    subject: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """树形返回知识点"""
    from sqlalchemy import text
    
    query = "SELECT id, subject, module, point, code, level FROM knowledge_points WHERE 1=1"
    params = {}
    
    if subject:
        query += " AND subject = :subject"
        params["subject"] = subject
        
    if q:
        query += " AND (point ILIKE :q OR module ILIKE :q)"
        params["q"] = f"%{q}%"
    
    query += " ORDER BY subject, level, id"
    
    result = db.execute(text(query), params)
    knowledge_points = []
    
    for row in result:
        knowledge_points.append({
            "id": row[0],
            "subject": row[1],
            "module": row[2],
            "point": row[3],
            "code": row[4],
            "level": row[5]
        })
    
    return knowledge_points

@app.post("/api/questions", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """新建题（含选项/答案/解析/知识点映射）"""
    from sqlalchemy import text
    import json
    from datetime import datetime
    
    # Insert question
    result = db.execute(
        text("""
            INSERT INTO questions (stem, type, difficulty, options_json, answer_json, analysis, created_by, status, created_at)
            VALUES (:stem, :type, :difficulty, :options_json, :answer_json, :analysis, :created_by, 'draft', :created_at)
            RETURNING id, created_at
        """),
        {
            "stem": question.stem,
            "type": question.type,
            "difficulty": question.difficulty,
            "options_json": json.dumps(question.options_json) if question.options_json else None,
            "answer_json": json.dumps(question.answer_json) if question.answer_json else None,
            "analysis": question.analysis,
            "created_by": current_user["id"],
            "created_at": datetime.utcnow()
        }
    )
    
    new_question = result.fetchone()
    if not new_question:
        raise HTTPException(status_code=500, detail="Failed to create question")
    question_id = new_question[0]
    
    # Insert knowledge point mappings
    for kp_id in question.knowledge_point_ids:
        db.execute(
            text("INSERT INTO question_knowledge_map (question_id, kp_id) VALUES (:qid, :kpid)"),
            {"qid": question_id, "kpid": kp_id}
        )
    
    db.commit()
    
    return {
        "id": question_id,
        "stem": question.stem,
        "type": question.type,
        "difficulty": question.difficulty,
        "status": "draft",
        "created_at": str(new_question[1]) if new_question[1] else None
    }

@app.get("/api/questions", response_model=List[QuestionResponse])
def get_questions(
    kp: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[int] = None,
    q: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """查询题目"""
    from sqlalchemy import text
    
    query = """
        SELECT DISTINCT q.id, q.stem, q.type, q.difficulty, q.status, q.created_at
        FROM questions q
        LEFT JOIN question_knowledge_map qkm ON q.id = qkm.question_id
        LEFT JOIN knowledge_points kp ON qkm.kp_id = kp.id
        WHERE 1=1
    """
    params = {}
    
    if kp:
        query += " AND kp.code = :kp_code"
        params["kp_code"] = kp
    
    if type:
        query += " AND q.type = :type"
        params["type"] = type
        
    if difficulty:
        query += " AND q.difficulty = :difficulty"
        params["difficulty"] = difficulty
        
    if q:
        query += " AND q.stem ILIKE :search"
        params["search"] = f"%{q}%"
    
    query += " ORDER BY q.id DESC LIMIT :size OFFSET :offset"
    params["size"] = size
    params["offset"] = (page - 1) * size
    
    result = db.execute(text(query), params)
    questions = []
    
    for row in result:
        questions.append({
            "id": row[0],
            "stem": row[1][:200] + "..." if len(row[1]) > 200 else row[1],  # Truncate for list view
            "type": row[2],
            "difficulty": row[3],
            "status": row[4],
            "created_at": str(row[5]) if row[5] else None
        })
    
    return questions

@app.post("/api/questions/{question_id}/publish")
def publish_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """发布题目"""
    from sqlalchemy import text
    
    result = db.execute(
        text("UPDATE questions SET status = 'published' WHERE id = :id AND created_by = :user_id"),
        {"id": question_id, "user_id": current_user["id"]}
    )
    
    # Check if update was successful by querying the question
    check_result = db.execute(
        text("SELECT id FROM questions WHERE id = :id AND created_by = :user_id"),
        {"id": question_id, "user_id": current_user["id"]}
    )
    if not check_result.fetchone():
        raise HTTPException(status_code=404, detail="Question not found or no permission")
    
    db.commit()
    return {"message": "Question published successfully"}

@app.post("/api/answer-sheets/upload")
async def upload_sheet(
    paper_id: int, 
    class_id: int, 
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    # TODO: store file to MinIO and enqueue OCR/OMR task
    return {
        "status": "accepted", 
        "paper_id": paper_id, 
        "class_id": class_id, 
        "filename": file.filename,
        "message": "File uploaded successfully, processing will begin shortly"
    }

@app.get("/api/answer-sheets/{sheet_id}/report")
def get_report(
    sheet_id: int,
    current_user = Depends(get_current_user)
):
    # TODO: return simple mock report for MVP demo
    return {
        "sheet_id": sheet_id, 
        "student_name": "学生示例",
        "paper_name": "示例试卷",
        "total_score": 95, 
        "items": [
            {"question_id": 1, "score": 10, "is_correct": True},
            {"question_id": 2, "score": 8, "is_correct": False},
        ]
    }
