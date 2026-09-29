import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    participants = relationship(
        "Participant", back_populates="session", cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense", back_populates="session", cascade="all, delete-orphan"
    )


class Participant(Base):
    __tablename__ = "participants"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    name = Column(String, nullable=False)

    session = relationship("Session", back_populates="participants")
    splits = relationship(
        "ExpenseSplit", back_populates="participant", cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by_id = Column(String, ForeignKey("participants.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("Session", back_populates="expenses")
    paid_by = relationship("Participant", foreign_keys=[paid_by_id])
    splits = relationship(
        "ExpenseSplit", back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(String, primary_key=True, default=generate_uuid)
    expense_id = Column(String, ForeignKey("expenses.id"), nullable=False)
    participant_id = Column(String, ForeignKey("participants.id"), nullable=False)
    amount_owed = Column(Float, nullable=False)

    expense = relationship("Expense", back_populates="splits")
    participant = relationship("Participant", back_populates="splits")
