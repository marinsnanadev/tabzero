from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------- Session ----------

class SessionCreate(BaseModel):
    name: str
    participant_names: list[str] = []


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    created_at: datetime


# ---------- Participant ----------

class ParticipantCreate(BaseModel):
    name: str


class ParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


# ---------- Expense ----------

class ExpenseSplitIn(BaseModel):
    participant_id: str
    amount_owed: Optional[float] = None  # se None, divide igualmente


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    paid_by_id: str
    splits: list[ExpenseSplitIn] = []  # vazio = divide igual entre todos os participantes


class ExpenseSplitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participant_id: str
    amount_owed: float


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str
    amount: float
    paid_by_id: str
    created_at: datetime
    splits: list[ExpenseSplitOut]


# ---------- Balance / Settlement ----------

class BalanceOut(BaseModel):
    participant_id: str
    name: str
    balance: float  # positivo = a receber, negativo = a pagar


class SettlementOut(BaseModel):
    from_id: str
    from_name: str
    to_id: str
    to_name: str
    amount: float
