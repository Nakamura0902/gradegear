# app/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas


# ===== Subject 関連 =====

def get_subjects(db: Session, skip: int = 0, limit: int = 100) -> List[models.Subject]:
    return db.query(models.Subject).offset(skip).limit(limit).all()


def get_subject(db: Session, subject_id: int) -> Optional[models.Subject]:
    return db.query(models.Subject).filter(models.Subject.id == subject_id).first()


def create_subject(db: Session, subject_in: schemas.SubjectCreate) -> models.Subject:
    db_subject = models.Subject(
        name=subject_in.name,
        teacher=subject_in.teacher,
        credit=subject_in.credit,
        day_of_week=subject_in.day_of_week,
        period=subject_in.period,
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int) -> bool:
    subject = get_subject(db, subject_id)
    if not subject:
        return False
    db.delete(subject)
    db.commit()
    return True


# ===== Task 関連 =====

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Task]:
    return db.query(models.Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks_by_subject(
    db: Session, subject_id: int, skip: int = 0, limit: int = 100
) -> List[models.Task]:
    return (
        db.query(models.Task)
        .filter(models.Task.subject_id == subject_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_task(db: Session, task_in: schemas.TaskCreate) -> models.Task:
    db_task = models.Task(
        subject_id=task_in.subject_id,
        name=task_in.name,
        type=task_in.type,
        weight=task_in.weight,
        score=task_in.score,
        date=task_in.date,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True







def calc_subject_summary(db: Session, subject_id: int) -> Optional[schemas.SubjectSummary]:
    subject = get_subject(db, subject_id)
    if subject is None:
        return None

    tasks = get_tasks_by_subject(db, subject_id=subject_id)

    # Task が1つもない場合
    if not tasks:
        return schemas.SubjectSummary(
            subject_id=subject.id,
            subject_name=subject.name,
            total_weight=0.0,
            scored_weight=0.0,
            current_score=None,
            predicted_final_score=None,
            grade=None,
        )

    # 全Taskの配点合計
    total_weight = sum(t.weight for t in tasks)

    # score が入っている Task だけ取り出す
    scored_tasks = [t for t in tasks if t.score is not None]
    scored_weight = sum(t.weight for t in scored_tasks)

    if scored_weight > 0:
        weighted_sum = sum(t.score * t.weight for t in scored_tasks)
        current_score = weighted_sum / scored_weight
    else:
        current_score = None

    if current_score is not None and total_weight > 0:
        # 今の平均点をそのまま最終予測として使う
        predicted_final_score = current_score
    else:
        predicted_final_score = None

    def to_grade(score: Optional[float]) -> Optional[str]:
        if score is None:
            return None
        if score >= 90:
            return "S"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        return "F"

    grade = to_grade(predicted_final_score)

    return schemas.SubjectSummary(
        subject_id=subject.id,
        subject_name=subject.name,
        total_weight=total_weight,
        scored_weight=scored_weight,
        current_score=current_score,
        predicted_final_score=predicted_final_score,
        grade=grade,
    )
def calc_needed_score(
    db: Session, subject_id: int, target_grade: str
) -> Optional[schemas.NeedScoreResult]:
    subject = get_subject(db, subject_id)
    if subject is None:
        return None

    tasks = get_tasks_by_subject(db, subject_id=subject_id)

    # 評価のしきい値
    grade_thresholds = {
        "S": 90.0,
        "A": 80.0,
        "B": 70.0,
        "C": 60.0,
        "F": 0.0,
    }

    target_grade = target_grade.upper()
    if target_grade not in grade_thresholds:
        # 対応していない評価
        raise ValueError("Invalid grade")

    target_score = grade_thresholds[target_grade]

    if not tasks:
        # Taskが無いと計算できない
        return schemas.NeedScoreResult(
            subject_id=subject.id,
            subject_name=subject.name,
            target_grade=target_grade,
            target_score=target_score,
            current_score=None,
            total_weight=0.0,
            scored_weight=0.0,
            remaining_weight=0.0,
            required_average_on_remaining=None,
            achievable=False,
            message="この科目にはまだ評価項目(Task)が登録されていません。",
        )

    total_weight = sum(t.weight for t in tasks)
    scored_tasks = [t for t in tasks if t.score is not None]
    scored_weight = sum(t.weight for t in scored_tasks)
    remaining_weight = total_weight - scored_weight

    weighted_sum = sum((t.score * t.weight) for t in scored_tasks)
    current_score = None
    if total_weight > 0:
        # 全配点に対する現在の予測点
        current_score = weighted_sum / total_weight

    # 残りの配点が0なら、もうこれ以上点数は動かない
    if remaining_weight <= 0:
        if current_score is not None and current_score >= target_score:
            return schemas.NeedScoreResult(
                subject_id=subject.id,
                subject_name=subject.name,
                target_grade=target_grade,
                target_score=target_score,
                current_score=current_score,
                total_weight=total_weight,
                scored_weight=scored_weight,
                remaining_weight=0.0,
                required_average_on_remaining=None,
                achievable=True,
                message="すでに目標の評価を達成しています。（残りの評価項目はありません）",
            )
        else:
            return schemas.NeedScoreResult(
                subject_id=subject.id,
                subject_name=subject.name,
                target_grade=target_grade,
                target_score=target_score,
                current_score=current_score,
                total_weight=total_weight,
                scored_weight=scored_weight,
                remaining_weight=0.0,
                required_average_on_remaining=None,
                achievable=False,
                message="残りの評価項目が無いため、これ以上成績を上げることはできません。",
            )

    # 残りの配点部分で平均x点取るとすると…
    # (weighted_sum + x * remaining_weight) / total_weight >= target_score
    # をみたす最小のxを求める
    required = (target_score * total_weight - weighted_sum) / remaining_weight

    # すでに目標到達している場合
    if required <= 0:
        return schemas.NeedScoreResult(
            subject_id=subject.id,
            subject_name=subject.name,
            target_grade=target_grade,
            target_score=target_score,
            current_score=current_score,
            total_weight=total_weight,
            scored_weight=scored_weight,
            remaining_weight=remaining_weight,
            required_average_on_remaining=0.0,
            achievable=True,
            message="すでに目標の評価に到達しています。残りは0点でも大丈夫です。",
        )

    # 100点を超える点数が必要なら「実質不可能」
    if required > 100:
        return schemas.NeedScoreResult(
            subject_id=subject.id,
            subject_name=subject.name,
            target_grade=target_grade,
            target_score=target_score,
            current_score=current_score,
            total_weight=total_weight,
            scored_weight=scored_weight,
            remaining_weight=remaining_weight,
            required_average_on_remaining=required,
            achievable=False,
            message="残りの評価項目で平均{:.1f}点が必要です。100点を超えているため、実質的に達成は困難です。".format(
                required
            ),
        )

    # 通常ケース：0～100の範囲で必要点を返す
    return schemas.NeedScoreResult(
        subject_id=subject.id,
        subject_name=subject.name,
        target_grade=target_grade,
        target_score=target_score,
        current_score=current_score,
        total_weight=total_weight,
        scored_weight=scored_weight,
        remaining_weight=remaining_weight,
        required_average_on_remaining=required,
        achievable=True,
        message="残りの評価項目で平均{:.1f}点以上を取れば目標の評価に到達できます。".format(
            required
        ),
    )
