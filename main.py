# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud
from .database import engine, Base, get_db
app = FastAPI()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GradeGear API",
    description="大学の科目・評価を管理する成績管理システムのAPI",
    version="0.2.0",
)


@app.get("/")
def read_root():
    return {"message": "GradeGear API 動いてるよ。/docs にアクセスしてみて。"}


# ===== Subject エンドポイント =====

@app.get("/subjects/", response_model=List[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = crud.get_subjects(db, skip=skip, limit=limit)
    return subjects


@app.get("/subjects/{subject_id}", response_model=schemas.Subject)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = crud.get_subject(db, subject_id=subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


# 既存: 科目1件取得
@app.get("/subjects/{subject_id}", response_model=schemas.Subject)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = crud.get_subject(db, subject_id=subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


# ★ 新規: 科目の成績サマリ
@app.get("/subjects/{subject_id}/summary", response_model=schemas.SubjectSummary)
def read_subject_summary(subject_id: int, db: Session = Depends(get_db)):
    summary = crud.calc_subject_summary(db, subject_id=subject_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return summary



@app.post("/subjects/", response_model=schemas.Subject)
def create_subject(subject_in: schemas.SubjectCreate, db: Session = Depends(get_db)):
    subject = crud.create_subject(db, subject_in=subject_in)
    return subject

@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    success = crud.delete_subject(db, subject_id=subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"ok": True}

# 科目の成績サマリは既にある想定
@app.get("/subjects/{subject_id}/summary", response_model=schemas.SubjectSummary)
def read_subject_summary(subject_id: int, db: Session = Depends(get_db)):
    summary = crud.calc_subject_summary(db, subject_id=subject_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return summary


# ★ 追加: 目標評価をとるために必要な点数
@app.get(
    "/subjects/{subject_id}/need/{target_grade}",
    response_model=schemas.NeedScoreResult,
)
def read_needed_score(
    subject_id: int, target_grade: str, db: Session = Depends(get_db)
):
    try:
        result = crud.calc_needed_score(db, subject_id=subject_id, target_grade=target_grade)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target grade")

    if result is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    return result



# ===== Task エンドポイント =====

# 全Task一覧
@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


# Task 1件取得
@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# 科目ごとの Task 一覧
@app.get("/subjects/{subject_id}/tasks/", response_model=List[schemas.Task])
def read_tasks_by_subject(
    subject_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    # 科目が存在するかチェック
    subject = crud.get_subject(db, subject_id=subject_id)
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    tasks = crud.get_tasks_by_subject(db, subject_id=subject_id, skip=skip, limit=limit)
    return tasks


# Task 作成
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)):
    # 科目が存在するかチェック
    subject = crud.get_subject(db, subject_id=task_in.subject_id)
    if subject is None:
        raise HTTPException(status_code=400, detail="Subject does not exist")

    task = crud.create_task(db, task_in=task_in)
    return task



# Task 削除
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


# ここを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 最初は雑に全部許可でOK（あとで絞れる）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
