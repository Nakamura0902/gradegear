# app/schemas.py

from __future__ import annotations   # ← この1行が超強力
import datetime 
from typing import Optional
from pydantic import BaseModel


# ---------- Subject 用 ----------

class SubjectBase(BaseModel):
    name: str
    teacher: Optional[str] = None
    credit: Optional[int] = None
    day_of_week: Optional[str] = None
    period: Optional[int] = None


class SubjectCreate(SubjectBase):
    pass


class Subject(SubjectBase):
    id: int

    class Config:
        orm_mode = True


# ---------- Task 用 ----------

class TaskBase(BaseModel):
    name: str
    type: str
    weight: float
    score: Optional[float] = None
    date: Optional[datetime.date] = None   # ← これで絶対エラー消える


class TaskCreate(TaskBase):
    subject_id: int


class Task(TaskBase):
    id: int
    subject_id: int

    class Config:
        orm_mode = True
# ---------- Subject Summary 用 ----------

class SubjectSummary(BaseModel):
    subject_id: int
    subject_name: str

    total_weight: float
    scored_weight: float
    current_score: Optional[float] = None
    predicted_final_score: Optional[float] = None
    grade: Optional[str] = None

    class Config:
        orm_mode = True

# ---------- 必要得点計算用 ----------

class NeedScoreResult(BaseModel):
    subject_id: int
    subject_name: str

    target_grade: str          # 目標: "S", "A", "B", "C"
    target_score: float        # 目標となる点数 (例: Aなら80)

    current_score: Optional[float] = None  # 今の予測点 (全Taskを100%埋めたと仮定)
    total_weight: float                     # 全Taskの配点合計
    scored_weight: float                    # すでに点数がついている配点
    remaining_weight: float                 # まだ点数がついていない配点

    required_average_on_remaining: Optional[float] = None
    # 残り部分で必要な平均点 (0〜100を想定)

    achievable: bool                         # 達成可能か
    message: str                             # 日本語メッセージ
