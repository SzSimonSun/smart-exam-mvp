from __future__ import annotations

from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import asc, or_
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .auth import get_current_active_user, get_teacher_user
from .database import get_db
from .models import (
    Answer,
    AnswerSheet,
    Class,
    ClassStudent,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgeMap,
    User,
)
from .routers import auth as auth_router
from .storage import store_answer_sheet_file
from .schemas import (
    AnswerResponse,
    AnswerSheetReport,
    AnswerSheetResponse,
    CurrentUser,
    KnowledgePointResponse,
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
)

app = FastAPI(title="Smart Exam System - MVP API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/users/me", response_model=CurrentUser)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> CurrentUser:
    return current_user


def _build_knowledge_point_tree(kps: List[KnowledgePoint]) -> List[KnowledgePointResponse]:
    nodes: dict[int, KnowledgePointResponse] = {}
    roots: List[KnowledgePointResponse] = []

    for kp in kps:
        node = KnowledgePointResponse.model_validate(kp, from_attributes=True)
        node = node.model_copy(update={"children": []})
        nodes[kp.id] = node

    for kp in kps:
        node = nodes[kp.id]
        if kp.parent_id and kp.parent_id in nodes:
            parent = nodes[kp.parent_id]
            parent.children.append(node)
        else:
            roots.append(node)

    return roots


@app.get(
    "/api/knowledge-points",
    response_model=List[KnowledgePointResponse],
)
def list_knowledge_points(
    subject: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> List[KnowledgePointResponse]:
    query = db.query(KnowledgePoint)

    if subject:
        query = query.filter(KnowledgePoint.subject == subject)

    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            or_(
                KnowledgePoint.point.ilike(like_pattern),
                KnowledgePoint.module.ilike(like_pattern),
            )
        )

    points = (
        query.order_by(
            KnowledgePoint.subject,
            asc(KnowledgePoint.level).nullsfirst(),
            KnowledgePoint.id,
        )
        .all()
    )

    return _build_knowledge_point_tree(points)


def _question_to_response(question: Question) -> QuestionResponse:
    kp_nodes = [
        KnowledgePointResponse.model_validate(
            mapping.knowledge_point, from_attributes=True
        )
        for mapping in question.knowledge_points
        if mapping.knowledge_point is not None
    ]

    return QuestionResponse(
        id=question.id,
        stem=question.stem,
        type=question.type,
        difficulty=question.difficulty,
        options_json=question.options_json,
        answer_json=question.answer_json,
        analysis=question.analysis,
        source_meta=question.source_meta,
        created_by=question.created_by,
        status=question.status,
        created_at=question.created_at,
        knowledge_points=kp_nodes,
    )


@app.post("/api/questions", response_model=QuestionResponse, status_code=201)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user),
) -> QuestionResponse:
    if not payload.knowledge_point_ids:
        raise HTTPException(status_code=400, detail="knowledge_point_ids cannot be empty")

    kps = (
        db.query(KnowledgePoint)
        .filter(KnowledgePoint.id.in_(payload.knowledge_point_ids))
        .all()
    )

    if len(kps) != len(set(payload.knowledge_point_ids)):
        raise HTTPException(status_code=404, detail="One or more knowledge points not found")

    question = Question(
        stem=payload.stem,
        type=payload.type,
        difficulty=payload.difficulty,
        options_json=payload.options_json,
        answer_json=payload.answer_json,
        analysis=payload.analysis,
        source_meta=payload.source_meta,
        created_by=current_user.id,
        status="draft",
    )

    db.add(question)
    db.flush()

    mappings = [
        QuestionKnowledgeMap(question_id=question.id, kp_id=kp.id) for kp in kps
    ]
    db.add_all(mappings)

    db.commit()
    db.refresh(question)

    return _question_to_response(question)


@app.get("/api/questions", response_model=QuestionListResponse)
def list_questions(
    kp: Optional[str] = None,
    type: Optional[str] = None,
    difficulty: Optional[int] = None,
    q: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> QuestionListResponse:
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="page and size must be positive integers")

    query = db.query(Question).options(
        selectinload(Question.knowledge_points).selectinload(
            QuestionKnowledgeMap.knowledge_point
        )
    )

    if kp:
        query = query.join(QuestionKnowledgeMap).join(KnowledgePoint).filter(
            KnowledgePoint.code == kp
        )

    if type:
        query = query.filter(Question.type == type)

    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)

    if q:
        query = query.filter(Question.stem.ilike(f"%{q}%"))

    filtered_query = query.distinct()
    total = filtered_query.count()

    items = (
        filtered_query.order_by(Question.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    responses = [_question_to_response(question) for question in items]

    return QuestionListResponse(items=responses, total=total, page=page, size=size)


@app.post("/api/questions/{question_id}/publish")
def publish_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user),
) -> dict:
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if current_user.role != "admin" and question.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to publish this question")

    question.status = "published"
    db.commit()

    return {"message": "Question published successfully"}

@app.post("/api/answer-sheets/upload", response_model=AnswerSheetResponse, status_code=201)
async def upload_answer_sheet(
    paper_id: int = Form(...),
    class_id: int = Form(...),
    student_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_user),
) -> AnswerSheetResponse:
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if class_obj is None:
        raise HTTPException(status_code=404, detail="Class not found")

    if current_user.role != "admin" and class_obj.owner_teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to upload for this class")

    if student_id is not None:
        membership = (
            db.query(ClassStudent)
            .filter(ClassStudent.class_id == class_id, ClassStudent.student_id == student_id)
            .first()
        )
        if membership is None:
            raise HTTPException(status_code=400, detail="Student is not enrolled in the class")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        object_name = store_answer_sheet_file(
            original_filename=file.filename or "upload.bin",
            data=file_bytes,
            content_type=file.content_type,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail="Failed to persist uploaded file") from exc

    sheet = AnswerSheet(
        paper_id=paper_id,
        student_id=student_id,
        class_id=class_id,
        qr_token=uuid4().hex,
        upload_uri=object_name,
        status="uploaded",
    )

    db.add(sheet)
    db.commit()
    db.refresh(sheet)

    return AnswerSheetResponse(
        id=sheet.id,
        paper_id=sheet.paper_id,
        student_id=sheet.student_id,
        class_id=sheet.class_id,
        status=sheet.status,
        created_at=sheet.created_at,
    )


@app.get("/api/answer-sheets/{sheet_id}/report", response_model=AnswerSheetReport)
def get_answer_sheet_report(
    sheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AnswerSheetReport:
    sheet = (
        db.query(AnswerSheet)
        .options(
            selectinload(AnswerSheet.answers),
            selectinload(AnswerSheet.paper),
            selectinload(AnswerSheet.student),
            selectinload(AnswerSheet.class_),
        )
        .filter(AnswerSheet.id == sheet_id)
        .first()
    )

    if sheet is None:
        raise HTTPException(status_code=404, detail="Answer sheet not found")

    if current_user.role == "teacher":
        if sheet.class_ is None or sheet.class_.owner_teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="No permission to view this report")
    elif current_user.role == "student":
        if sheet.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="No permission to view this report")

    answers: List[Answer] = sheet.answers or []
    total_score = Decimal("0")
    for answer in answers:
        total_score += answer.score or Decimal("0")

    answer_responses = [
        AnswerResponse(
            id=answer.id,
            question_id=answer.question_id,
            parsed_json=answer.parsed_json,
            is_objective=answer.is_objective,
            is_correct=answer.is_correct,
            score=answer.score,
            error_flag=answer.error_flag,
        )
        for answer in answers
    ]

    return AnswerSheetReport(
        sheet_id=sheet.id,
        student_name=sheet.student.name if sheet.student else "未指定学生",
        paper_name=sheet.paper.name if sheet.paper else "未匹配试卷",
        total_score=total_score,
        answers=answer_responses,
    )
