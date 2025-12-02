# app/models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    teacher = Column(String, nullable=True)
    credit = Column(Integer, default=2)
    day_of_week = Column(String, nullable=True)  # 月, 火, ...
    period = Column(Integer, nullable=True)      # 時限

    tasks = relationship("Task", back_populates="subject", cascade="all, delete-orphan")
    # logs = relationship("StudyLog", back_populates="subject")  ←あとで使う用


class Task(Base):
    """
    評価項目テーブル
    例: 期末テスト, レポート1, 小テスト3回目…
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))

    name = Column(String)          # 「第1回小テスト」など
    type = Column(String)          # "test", "report", "quiz" など
    weight = Column(Float)         # 配点(%) 例: 40.0
    score = Column(Float, nullable=True)  # 得点(100点満点換算) 未入力なら None
    date = Column(Date, nullable=True)    # 実施日 or 締切日

    subject = relationship("Subject", back_populates="tasks")
