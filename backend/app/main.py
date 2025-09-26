
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
import hashlib
import json
from datetime import datetime

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

class UploadResponse(BaseModel):
    session_id: str
    status: str
    message: str
    file_count: int = 0

class CallbackRequest(BaseModel):
    session_id: str
    status: str  # 'processing', 'completed', 'failed'
    progress: Optional[int] = None
    results: Optional[dict] = None
    error_message: Optional[str] = None

class IngestItem(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = 'medium'
    knowledge_points: List[str] = []
    confidence_score: Optional[float] = None

class IngestCallback(BaseModel):
    session_id: str
    status: str  # 'success', 'partial', 'failed'
    items: List[IngestItem] = []
    total_processed: int = 0
    success_count: int = 0
    error_count: int = 0
    error_message: Optional[str] = None

class PaperCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject: str
    grade: str
    duration: int = 90  # minutes
    total_score: int = 100
    question_ids: List[int] = []

class PaperResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    subject: str
    grade: str
    duration: int
    total_score: int
    status: str
    created_at: str

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
    # For MVP, using simple comparison - in production, use proper bcrypt hashing
    # Since we're using 'password' as the default password in test data
    return plain_password == 'password' or stored_password == plain_password

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

# 3.3 试卷管理
@app.get("/api/papers", response_model=List[PaperResponse])
def get_papers(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取试卷列表"""
    from sqlalchemy import text
    
    query = """
        SELECT id, name, description, subject, grade, duration, total_score, status, created_at
        FROM papers
        WHERE created_by = :user_id
    """
    params = {"user_id": current_user["id"]}
    
    if subject:
        query += " AND subject = :subject"
        params["subject"] = subject
        
    if grade:
        query += " AND grade = :grade"
        params["grade"] = grade
        
    if q:
        query += " AND name ILIKE :search"
        params["search"] = f"%{q}%"
    
    query += " ORDER BY created_at DESC LIMIT :size OFFSET :offset"
    params["size"] = size
    params["offset"] = (page - 1) * size
    
    result = db.execute(text(query), params)
    papers = []
    
    for row in result:
        papers.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "subject": row[3],
            "grade": row[4],
            "duration": row[5],
            "total_score": row[6],
            "status": row[7],
            "created_at": str(row[8]) if row[8] else None
        })
    
    return papers

@app.post("/api/papers", response_model=PaperResponse)
def create_paper(
    paper: PaperCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建试卷"""
    from sqlalchemy import text
    from datetime import datetime
    
    # Insert paper
    result = db.execute(
        text("""
            INSERT INTO papers (name, description, subject, grade, duration, total_score, created_by, status, created_at)
            VALUES (:name, :description, :subject, :grade, :duration, :total_score, :created_by, 'draft', :created_at)
            RETURNING id, created_at
        """),
        {
            "name": paper.name,
            "description": paper.description,
            "subject": paper.subject,
            "grade": paper.grade,
            "duration": paper.duration,
            "total_score": paper.total_score,
            "created_by": current_user["id"],
            "created_at": datetime.utcnow()
        }
    )
    
    new_paper = result.fetchone()
    if not new_paper:
        raise HTTPException(status_code=500, detail="Failed to create paper")
    paper_id = new_paper[0]
    
    # Insert question mappings if provided
    for question_id in paper.question_ids:
        db.execute(
            text("INSERT INTO paper_questions (paper_id, question_id) VALUES (:paper_id, :question_id)"),
            {"paper_id": paper_id, "question_id": question_id}
        )
    
    db.commit()
    
    return {
        "id": paper_id,
        "name": paper.name,
        "description": paper.description,
        "subject": paper.subject,
        "grade": paper.grade,
        "duration": paper.duration,
        "total_score": paper.total_score,
        "status": "draft",
        "created_at": str(new_paper[1]) if new_paper[1] else None
    }

@app.get("/api/papers/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取试卷详情"""
    from sqlalchemy import text
    
    result = db.execute(
        text("""
            SELECT id, name, description, subject, grade, duration, total_score, status, created_at
            FROM papers
            WHERE id = :id AND created_by = :user_id
        """),
        {"id": paper_id, "user_id": current_user["id"]}
    )
    
    paper = result.fetchone()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return {
        "id": paper[0],
        "name": paper[1],
        "description": paper[2],
        "subject": paper[3],
        "grade": paper[4],
        "duration": paper[5],
        "total_score": paper[6],
        "status": paper[7],
        "created_at": str(paper[8]) if paper[8] else None
    }

@app.post("/api/papers/{paper_id}/export")
def export_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """导出试卷PDF (Mock)"""
    # TODO: 实现真正的PDF导出
    return {
        "message": "PDF export functionality will be implemented",
        "paper_id": paper_id,
        "download_url": f"/api/papers/{paper_id}/download"
    }

@app.post("/api/papers/{paper_id}/duplicate")
def duplicate_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """复制试卷"""
    from sqlalchemy import text
    from datetime import datetime
    
    # Get original paper
    result = db.execute(
        text("""
            SELECT name, description, subject, grade, duration, total_score
            FROM papers
            WHERE id = :id AND created_by = :user_id
        """),
        {"id": paper_id, "user_id": current_user["id"]}
    )
    
    original_paper = result.fetchone()
    if not original_paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Create duplicate
    new_result = db.execute(
        text("""
            INSERT INTO papers (name, description, subject, grade, duration, total_score, created_by, status, created_at)
            VALUES (:name, :description, :subject, :grade, :duration, :total_score, :created_by, 'draft', :created_at)
            RETURNING id
        """),
        {
            "name": f"{original_paper[0]} (副本)",
            "description": original_paper[1],
            "subject": original_paper[2],
            "grade": original_paper[3],
            "duration": original_paper[4],
            "total_score": original_paper[5],
            "created_by": current_user["id"],
            "created_at": datetime.utcnow()
        }
    )
    
    new_paper = new_result.fetchone()
    if not new_paper:
        raise HTTPException(status_code=500, detail="Failed to duplicate paper")
    new_paper_id = new_paper[0]
    
    # Copy questions
    db.execute(
        text("""
            INSERT INTO paper_questions (paper_id, question_id)
            SELECT :new_paper_id, question_id
            FROM paper_questions
            WHERE paper_id = :original_paper_id
        """),
        {"new_paper_id": new_paper_id, "original_paper_id": paper_id}
    )
    
    db.commit()
    
    return {
        "id": new_paper_id,
        "message": "Paper duplicated successfully"
    }

# 3.4 回调接口（供OCR/OMR服务调用）
@app.post("/api/callbacks/upload-progress")
def upload_progress_callback(callback: CallbackRequest):
    """
    文件上传进度回调
    OCR/OMR服务调用此接口报告处理进度
    """
    from sqlalchemy import text
    
    # 模拟数据库连接（实际项目中应该用依赖注入）
    import sqlite3
    conn = sqlite3.connect('test_exam.db')
    cursor = conn.cursor()
    
    try:
        # 更新上传会话状态
        cursor.execute("""
            UPDATE upload_sessions 
            SET status = ?, progress = ?, updated_at = CURRENT_TIMESTAMP,
                error_message = ?, results_json = ?
            WHERE session_id = ?
        """, (
            callback.status,
            callback.progress,
            callback.error_message,
            json.dumps(callback.results) if callback.results else None,
            callback.session_id
        ))
        
        # 如果处理完成，创建答题卡记录
        if callback.status == 'completed' and callback.results:
            results = callback.results
            if 'sheets' in results:
                for sheet_data in results['sheets']:
                    cursor.execute("""
                        INSERT INTO answer_sheets (paper_id, student_id, class_id, qr_token, upload_uri, status)
                        VALUES (?, ?, ?, ?, ?, 'processed')
                    """, (
                        sheet_data.get('paper_id'),
                        sheet_data.get('student_id'),
                        sheet_data.get('class_id'),
                        sheet_data.get('qr_token'),
                        sheet_data.get('image_url')
                    ))
                    
                    sheet_id = cursor.lastrowid
                    
                    # 插入答案数据
                    if 'answers' in sheet_data:
                        for answer_data in sheet_data['answers']:
                            cursor.execute("""
                                INSERT INTO answers (sheet_id, question_id, raw_omr, raw_ocr, 
                                                   parsed_json, is_correct, score)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                sheet_id,
                                answer_data.get('question_id'),
                                answer_data.get('raw_omr'),
                                answer_data.get('raw_ocr'),
                                json.dumps(answer_data.get('parsed_answer')),
                                answer_data.get('is_correct'),
                                answer_data.get('score')
                            ))
        
        conn.commit()
        return {"status": "success", "message": "Callback processed successfully"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Callback processing failed: {str(e)}")
    finally:
        conn.close()

@app.post("/api/callbacks/ingest-result")
def ingest_result_callback(callback: IngestCallback):
    """
    拆题入库结果回调
    AI拆题服务调用此接口提交拆题结果
    """
    import sqlite3
    conn = sqlite3.connect('test_exam.db')
    cursor = conn.cursor()
    
    try:
        # 更新拆题会话状态
        cursor.execute("""
            UPDATE ingest_sessions 
            SET status = ?, total_items = ?, processed_items = ?, 
                success_count = ?, error_count = ?, updated_at = CURRENT_TIMESTAMP,
                error_message = ?
            WHERE session_id = ?
        """, (
            callback.status,
            callback.total_processed,
            callback.total_processed,
            callback.success_count,
            callback.error_count,
            callback.error_message,
            callback.session_id
        ))
        
        # 插入拆题结果
        for item in callback.items:
            cursor.execute("""
                INSERT INTO ingest_items (session_id, question_text, question_type, 
                                         options_json, correct_answer, explanation, 
                                         difficulty, knowledge_points_json, 
                                         confidence_score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                callback.session_id,
                item.question_text,
                item.question_type,
                json.dumps(item.options) if item.options else None,
                item.correct_answer,
                item.explanation,
                item.difficulty,
                json.dumps(item.knowledge_points),
                item.confidence_score
            ))
        
        conn.commit()
        return {
            "status": "success", 
            "message": f"Processed {len(callback.items)} items successfully",
            "session_id": callback.session_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ingest callback failed: {str(e)}")
    finally:
        conn.close()

@app.post("/api/callbacks/grading-result")
def grading_result_callback(
    sheet_id: int,
    results: dict,
    background_tasks: BackgroundTasks
):
    """
    阅卷结果回调
    自动阅卷服务调用此接口提交阅卷结果
    """
    import sqlite3
    
    def update_grading_results():
        conn = sqlite3.connect('test_exam.db')
        cursor = conn.cursor()
        
        try:
            # 更新答题卡状态
            cursor.execute("""
                UPDATE answer_sheets 
                SET status = 'graded', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (sheet_id,))
            
            # 更新答案得分
            for question_id, result in results.get('answers', {}).items():
                cursor.execute("""
                    UPDATE answers 
                    SET is_correct = ?, score = ?, 
                        ai_confidence = ?, graded_at = CURRENT_TIMESTAMP
                    WHERE sheet_id = ? AND question_id = ?
                """, (
                    result.get('is_correct'),
                    result.get('score'),
                    result.get('confidence'),
                    sheet_id,
                    question_id
                ))
            
            # 计算总分
            cursor.execute("""
                SELECT COALESCE(SUM(score), 0) as total_score
                FROM answers WHERE sheet_id = ?
            """, (sheet_id,))
            
            total_score = cursor.fetchone()[0]
            
            # 更新总分
            cursor.execute("""
                UPDATE answer_sheets 
                SET total_score = ?
                WHERE id = ?
            """, (total_score, sheet_id))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Grading callback error: {str(e)}")
        finally:
            conn.close()
    
    # 在后台处理，避免阻塞回调响应
    background_tasks.add_task(update_grading_results)
    
    return {
        "status": "accepted",
        "message": "Grading results received and processing",
        "sheet_id": sheet_id
    }
