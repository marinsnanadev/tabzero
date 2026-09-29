"""
Lógica pura (sem dependência de banco/HTTP) para:
1. Calcular o saldo líquido de cada participante.
2. Simplificar as dívidas do grupo no menor número possível de transferências.
"""

from dataclasses import dataclass


@dataclass
class Balance:
    participant_id: str
    name: str
    balance: float  # positivo = a receber, negativo = a pagar


@dataclass
class Settlement:
    from_id: str
    from_name: str
    to_id: str
    to_name: str
    amount: float


def calculate_balances(participants: list[dict], expenses: list[dict]) -> list[Balance]:
    """
    participants: [{"id": str, "name": str}, ...]
    expenses: [{
        "paid_by_id": str,
        "amount": float,
        "splits": [{"participant_id": str, "amount_owed": float}, ...]
    }, ...]

    Saldo = total pago - total devido.
    """
    balance_by_id = {p["id"]: 0.0 for p in participants}

    for expense in expenses:
        balance_by_id[expense["paid_by_id"]] += expense["amount"]
        for split in expense["splits"]:
            balance_by_id[split["participant_id"]] -= split["amount_owed"]

    names_by_id = {p["id"]: p["name"] for p in participants}
    return [
        Balance(participant_id=pid, name=names_by_id[pid], balance=round(bal, 2))
        for pid, bal in balance_by_id.items()
    ]


def simplify_debts(balances: list[Balance], epsilon: float = 0.01) -> list[Settlement]:
    """
    Algoritmo guloso: a cada passo, casa quem mais deve com quem mais tem a
    receber, gerando o menor número de transferências para zerar todos os
    saldos. Complexidade O(n log n).

    Importante: não muta a lista `balances` recebida — trabalha sobre cópias
    locais (id -> saldo restante), já que os objetos `Balance` originais
    podem ser reutilizados pelo chamador (ex: para exibir o saldo real na
    tela) depois desta chamada.
    """
    remaining = {b.participant_id: b.balance for b in balances}
    names = {b.participant_id: b.name for b in balances}

    debtor_ids = sorted(
        [pid for pid, bal in remaining.items() if bal < -epsilon],
        key=lambda pid: remaining[pid],
    )
    creditor_ids = sorted(
        [pid for pid, bal in remaining.items() if bal > epsilon],
        key=lambda pid: remaining[pid],
        reverse=True,
    )

    settlements: list[Settlement] = []
    i, j = 0, 0

    while i < len(debtor_ids) and j < len(creditor_ids):
        debtor_id = debtor_ids[i]
        creditor_id = creditor_ids[j]

        amount = min(-remaining[debtor_id], remaining[creditor_id])
        amount = round(amount, 2)

        if amount > epsilon:
            settlements.append(
                Settlement(
                    from_id=debtor_id,
                    from_name=names[debtor_id],
                    to_id=creditor_id,
                    to_name=names[creditor_id],
                    amount=amount,
                )
            )

        remaining[debtor_id] = round(remaining[debtor_id] + amount, 2)
        remaining[creditor_id] = round(remaining[creditor_id] - amount, 2)

        if abs(remaining[debtor_id]) <= epsilon:
            i += 1
        if abs(remaining[creditor_id]) <= epsilon:
            j += 1

    return settlements
