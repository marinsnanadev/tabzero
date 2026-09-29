def create_session_with_participants(client, names):
    response = client.post(
        "/sessions", json={"name": "Viagem praia", "participant_names": names}
    )
    assert response.status_code == 201
    return response.json()


def test_create_session_generates_unique_slug(client):
    session = create_session_with_participants(client, ["Ana", "Bruno"])
    assert session["slug"].startswith("viagem-praia-")

    response = client.get(f"/sessions/{session['slug']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Viagem praia"


def test_get_unknown_session_returns_404(client):
    response = client.get("/sessions/nao-existe")
    assert response.status_code == 404


def test_add_participant(client):
    session = create_session_with_participants(client, ["Ana"])
    response = client.post(
        f"/sessions/{session['slug']}/participants", json={"name": "Bruno"}
    )
    assert response.status_code == 201

    participants = client.get(f"/sessions/{session['slug']}/participants").json()
    names = {p["name"] for p in participants}
    assert names == {"Ana", "Bruno"}


def test_create_expense_with_equal_split(client):
    session = create_session_with_participants(client, ["Ana", "Bruno", "Carla"])
    participants = client.get(f"/sessions/{session['slug']}/participants").json()
    ana_id = next(p["id"] for p in participants if p["name"] == "Ana")

    response = client.post(
        f"/sessions/{session['slug']}/expenses",
        json={"description": "Jantar", "amount": 90.0, "paid_by_id": ana_id},
    )
    assert response.status_code == 201
    expense = response.json()
    assert len(expense["splits"]) == 3
    assert all(s["amount_owed"] == 30.0 for s in expense["splits"])


def test_create_expense_with_manual_split_must_sum_to_amount(client):
    session = create_session_with_participants(client, ["Ana", "Bruno"])
    participants = client.get(f"/sessions/{session['slug']}/participants").json()
    ana_id = participants[0]["id"]
    bruno_id = participants[1]["id"]

    response = client.post(
        f"/sessions/{session['slug']}/expenses",
        json={
            "description": "Uber",
            "amount": 50.0,
            "paid_by_id": ana_id,
            "splits": [
                {"participant_id": ana_id, "amount_owed": 20.0},
                {"participant_id": bruno_id, "amount_owed": 20.0},  # soma 40, deveria ser 50
            ],
        },
    )
    assert response.status_code == 400


def test_balances_and_settlements_end_to_end(client):
    session = create_session_with_participants(client, ["Ana", "Bruno", "Carla"])
    participants = client.get(f"/sessions/{session['slug']}/participants").json()
    ana_id = next(p["id"] for p in participants if p["name"] == "Ana")

    client.post(
        f"/sessions/{session['slug']}/expenses",
        json={"description": "Jantar", "amount": 90.0, "paid_by_id": ana_id},
    )

    balances = client.get(f"/sessions/{session['slug']}/balances").json()
    balance_by_name = {b["name"]: b["balance"] for b in balances}
    assert balance_by_name == {"Ana": 60.0, "Bruno": -30.0, "Carla": -30.0}

    settlements = client.get(f"/sessions/{session['slug']}/settlements").json()
    assert len(settlements) == 2
    assert all(s["to_name"] == "Ana" for s in settlements)
    assert sum(s["amount"] for s in settlements) == 60.0


def test_expense_with_paid_by_outside_session_is_rejected(client):
    session = create_session_with_participants(client, ["Ana"])
    response = client.post(
        f"/sessions/{session['slug']}/expenses",
        json={
            "description": "Gasto inválido",
            "amount": 10.0,
            "paid_by_id": "id-que-nao-existe",
        },
    )
    assert response.status_code == 400
