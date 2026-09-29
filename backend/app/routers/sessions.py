from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession, joinedload

from app import models, schemas
from app.calculations import calculate_balances, simplify_debts
from app.database import get_db
from app.utils import generate_unique_slug

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_session_or_404(db: DBSession, slug: str) -> models.Session:
    session = (
        db.query(models.Session)
        .options(joinedload(models.Session.participants))
        .filter(models.Session.slug == slug)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return session


# ---------- Sessions ----------

@router.post("", response_model=schemas.SessionOut, status_code=201)
def create_session(payload: schemas.SessionCreate, db: DBSession = Depends(get_db)):
    slug = generate_unique_slug(db, payload.name)
    session = models.Session(name=payload.name, slug=slug)
    db.add(session)
    db.flush()  # garante session.id antes de criar participantes

    for name in payload.participant_names:
        db.add(models.Participant(session_id=session.id, name=name))

    db.commit()
    db.refresh(session)
    return session


@router.get("/{slug}", response_model=schemas.SessionOut)
def get_session(slug: str, db: DBSession = Depends(get_db)):
    return _get_session_or_404(db, slug)


# ---------- Participants ----------

@router.post(
    "/{slug}/participants", response_model=schemas.ParticipantOut, status_code=201
)
def add_participant(
    slug: str, payload: schemas.ParticipantCreate, db: DBSession = Depends(get_db)
):
    session = _get_session_or_404(db, slug)
    participant = models.Participant(session_id=session.id, name=payload.name)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@router.get("/{slug}/participants", response_model=list[schemas.ParticipantOut])
def list_participants(slug: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, slug)
    return session.participants


# ---------- Expenses ----------

@router.post("/{slug}/expenses", response_model=schemas.ExpenseOut, status_code=201)
def create_expense(
    slug: str, payload: schemas.ExpenseCreate, db: DBSession = Depends(get_db)
):
    session = _get_session_or_404(db, slug)
    participant_ids = {p.id for p in session.participants}

    if payload.paid_by_id not in participant_ids:
        raise HTTPException(
            status_code=400, detail="paid_by_id não pertence a esta sessão"
        )

    resolved_splits: list[schemas.ExpenseSplitIn]

    if not payload.splits:
        # divisão igualitária entre todos os participantes da sessão
        if not session.participants:
            raise HTTPException(
                status_code=400, detail="Sessão não tem participantes para dividir o gasto"
            )
        share = round(payload.amount / len(session.participants), 2)
        resolved_splits = [
            schemas.ExpenseSplitIn(participant_id=p.id, amount_owed=share)
            for p in session.participants
        ]
        # ajusta arredondamento residual no último participante
        diff = round(payload.amount - share * len(session.participants), 2)
        if diff != 0:
            resolved_splits[-1].amount_owed = round(
                resolved_splits[-1].amount_owed + diff, 2
            )
    else:
        for split in payload.splits:
            if split.participant_id not in participant_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"participant_id {split.participant_id} não pertence a esta sessão",
                )
            if split.amount_owed is None:
                raise HTTPException(
                    status_code=400,
                    detail="amount_owed é obrigatório quando splits é informado manualmente",
                )
        total_split = round(sum(s.amount_owed for s in payload.splits), 2)
        if abs(total_split - round(payload.amount, 2)) > 0.02:
            raise HTTPException(
                status_code=400,
                detail=f"Soma dos splits ({total_split}) não bate com o valor do gasto ({payload.amount})",
            )
        resolved_splits = payload.splits

    expense = models.Expense(
        session_id=session.id,
        description=payload.description,
        amount=payload.amount,
        paid_by_id=payload.paid_by_id,
    )
    db.add(expense)
    db.flush()

    for split in resolved_splits:
        db.add(
            models.ExpenseSplit(
                expense_id=expense.id,
                participant_id=split.participant_id,
                amount_owed=split.amount_owed,
            )
        )

    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{slug}/expenses", response_model=list[schemas.ExpenseOut])
def list_expenses(slug: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, slug)
    return session.expenses


# ---------- Balances & Settlements ----------

@router.get("/{slug}/balances", response_model=list[schemas.BalanceOut])
def get_balances(slug: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, slug)

    participants = [{"id": p.id, "name": p.name} for p in session.participants]
    expenses = [
        {
            "paid_by_id": e.paid_by_id,
            "amount": e.amount,
            "splits": [
                {"participant_id": s.participant_id, "amount_owed": s.amount_owed}
                for s in e.splits
            ],
        }
        for e in session.expenses
    ]

    balances = calculate_balances(participants, expenses)
    return [
        schemas.BalanceOut(
            participant_id=b.participant_id, name=b.name, balance=b.balance
        )
        for b in balances
    ]


@router.get("/{slug}/settlements", response_model=list[schemas.SettlementOut])
def get_settlements(slug: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, slug)

    participants = [{"id": p.id, "name": p.name} for p in session.participants]
    expenses = [
        {
            "paid_by_id": e.paid_by_id,
            "amount": e.amount,
            "splits": [
                {"participant_id": s.participant_id, "amount_owed": s.amount_owed}
                for s in e.splits
            ],
        }
        for e in session.expenses
    ]

    balances = calculate_balances(participants, expenses)
    settlements = simplify_debts(balances)
    return [
        schemas.SettlementOut(
            from_id=s.from_id,
            from_name=s.from_name,
            to_id=s.to_id,
            to_name=s.to_name,
            amount=s.amount,
        )
        for s in settlements
    ]
