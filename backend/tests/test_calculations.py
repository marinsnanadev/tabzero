from app.calculations import calculate_balances, simplify_debts


PARTICIPANTS = [
    {"id": "a", "name": "Ana"},
    {"id": "b", "name": "Bruno"},
    {"id": "c", "name": "Carla"},
]


def test_balance_split_equally_among_three():
    expenses = [
        {
            "paid_by_id": "a",
            "amount": 90.0,
            "splits": [
                {"participant_id": "a", "amount_owed": 30.0},
                {"participant_id": "b", "amount_owed": 30.0},
                {"participant_id": "c", "amount_owed": 30.0},
            ],
        }
    ]
    balances = calculate_balances(PARTICIPANTS, expenses)
    balance_by_id = {b.participant_id: b.balance for b in balances}

    assert balance_by_id["a"] == 60.0  # pagou 90, deve 30
    assert balance_by_id["b"] == -30.0
    assert balance_by_id["c"] == -30.0


def test_balance_with_unequal_split():
    expenses = [
        {
            "paid_by_id": "a",
            "amount": 100.0,
            "splits": [
                {"participant_id": "a", "amount_owed": 20.0},
                {"participant_id": "b", "amount_owed": 80.0},
            ],
        }
    ]
    balances = calculate_balances(PARTICIPANTS, expenses)
    balance_by_id = {b.participant_id: b.balance for b in balances}

    assert balance_by_id["a"] == 80.0
    assert balance_by_id["b"] == -80.0
    assert balance_by_id["c"] == 0.0


def test_simplify_debts_single_transaction_for_two_people():
    expenses = [
        {
            "paid_by_id": "a",
            "amount": 90.0,
            "splits": [
                {"participant_id": "a", "amount_owed": 30.0},
                {"participant_id": "b", "amount_owed": 30.0},
                {"participant_id": "c", "amount_owed": 30.0},
            ],
        }
    ]
    balances = calculate_balances(PARTICIPANTS, expenses)
    settlements = simplify_debts(balances)

    # Ana recebe de Bruno e de Carla: 2 transferências
    assert len(settlements) == 2
    total_transferred = sum(s.amount for s in settlements)
    assert total_transferred == 60.0


def test_simplify_debts_reduces_transaction_count_vs_naive():
    """
    Cenário clássico: A pagou por B, B pagou por C, C pagou por A.
    Ingenuamente seriam 3 transferências; o algoritmo deve reduzir para no
    máximo 2 (ou 0, se os valores se cancelarem exatamente).
    """
    expenses = [
        {
            "paid_by_id": "a",
            "amount": 30.0,
            "splits": [{"participant_id": "b", "amount_owed": 30.0}],
        },
        {
            "paid_by_id": "b",
            "amount": 30.0,
            "splits": [{"participant_id": "c", "amount_owed": 30.0}],
        },
        {
            "paid_by_id": "c",
            "amount": 30.0,
            "splits": [{"participant_id": "a", "amount_owed": 30.0}],
        },
    ]
    balances = calculate_balances(PARTICIPANTS, expenses)
    settlements = simplify_debts(balances)

    # Todo mundo pagou e deve exatamente 30 -> saldo líquido zero para todos
    assert len(settlements) == 0


def test_simplify_debts_already_settled_returns_empty():
    balances = calculate_balances(
        PARTICIPANTS,
        expenses=[
            {
                "paid_by_id": "a",
                "amount": 30.0,
                "splits": [{"participant_id": "a", "amount_owed": 30.0}],
            }
        ],
    )
    settlements = simplify_debts(balances)
    assert settlements == []


def test_simplify_debts_total_amount_conserved():
    """
    Regressão: o total transferido nas settlements deve sempre igualar a
    soma dos saldos positivos (a soma dos negativos é o espelho). Esse teste
    reintroduz o cenário que quebraria se o algoritmo de casamento guloso
    tivesse um erro de arredondamento (ex: usar '<' em vez de '<=' no
    epsilon, deixando resíduos de centavos sem gerar transferência).
    """
    expenses = [
        {
            "paid_by_id": "a",
            "amount": 100.0,
            "splits": [
                {"participant_id": "a", "amount_owed": 33.33},
                {"participant_id": "b", "amount_owed": 33.33},
                {"participant_id": "c", "amount_owed": 33.34},
            ],
        }
    ]
    balances = calculate_balances(PARTICIPANTS, expenses)
    total_positive = sum(b.balance for b in balances if b.balance > 0)

    settlements = simplify_debts(balances)
    total_settled = sum(s.amount for s in settlements)

    # Regressão: balances não pode ser mutado por simplify_debts
    assert sum(b.balance for b in balances if b.balance > 0) == total_positive

    assert abs(total_positive - total_settled) < 0.02
