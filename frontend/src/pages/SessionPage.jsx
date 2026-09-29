import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api.js";

export default function SessionPage() {
  const { slug } = useParams();

  const [session, setSession] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [balances, setBalances] = useState([]);
  const [settlements, setSettlements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    try {
      const [sessionData, participantsData, expensesData, balancesData, settlementsData] =
        await Promise.all([
          api.getSession(slug),
          api.listParticipants(slug),
          api.listExpenses(slug),
          api.getBalances(slug),
          api.getSettlements(slug),
        ]);
      setSession(sessionData);
      setParticipants(participantsData);
      setExpenses(expensesData);
      setBalances(balancesData);
      setSettlements(settlementsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    reload();
  }, [reload]);

  if (loading) return <p className="muted">Carregando...</p>;
  if (error) return <div className="error">{error}</div>;

  return (
    <>
      <h1>{session.name}</h1>
      <div className="share-box">
        Link para compartilhar: <strong>{window.location.href}</strong>
      </div>

      <ParticipantsCard
        participants={participants}
        slug={slug}
        onChanged={reload}
      />

      <AddExpenseCard
        participants={participants}
        slug={slug}
        onChanged={reload}
      />

      <ExpensesCard expenses={expenses} participants={participants} />

      <BalancesCard balances={balances} />

      <SettlementsCard settlements={settlements} />
    </>
  );
}

function nameById(participants, id) {
  return participants.find((p) => p.id === id)?.name || "?";
}

function ParticipantsCard({ participants, slug, onChanged }) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAdd(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError("");
    try {
      await api.addParticipant(slug, name.trim());
      setName("");
      await onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <strong>Participantes</strong>
      {participants.map((p) => (
        <div key={p.id} className="list-item">
          <span>{p.name}</span>
        </div>
      ))}
      <form className="row" onSubmit={handleAdd} style={{ marginTop: 10 }}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome do novo participante"
          style={{ marginBottom: 0 }}
        />
        <button type="submit" disabled={loading}>
          Adicionar
        </button>
      </form>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

function AddExpenseCard({ participants, slug, onChanged }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [paidById, setPaidById] = useState("");
  const [manualSplit, setManualSplit] = useState(false);
  const [manualAmounts, setManualAmounts] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleManualSplit() {
    setManualSplit((prev) => !prev);
    setManualAmounts({});
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const parsedAmount = parseFloat(amount);
    if (!description.trim() || !parsedAmount || !paidById) {
      setError("Preencha descrição, valor e quem pagou.");
      return;
    }

    let splits = [];
    if (manualSplit) {
      splits = participants
        .map((p) => ({
          participant_id: p.id,
          amount_owed: parseFloat(manualAmounts[p.id] || "0"),
        }))
        .filter((s) => s.amount_owed > 0);
    }

    setLoading(true);
    try {
      await api.createExpense(slug, {
        description: description.trim(),
        amount: parsedAmount,
        paidById,
        splits,
      });
      setDescription("");
      setAmount("");
      setManualAmounts({});
      await onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <strong>Lançar gasto</strong>
      <form onSubmit={handleSubmit} style={{ marginTop: 10 }}>
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descrição (ex: Jantar)"
        />
        <input
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Valor total (ex: 90.00)"
          inputMode="decimal"
        />
        <select value={paidById} onChange={(e) => setPaidById(e.target.value)}>
          <option value="">Quem pagou?</option>
          {participants.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        <label className="row" style={{ marginBottom: 10 }}>
          <input
            type="checkbox"
            checked={manualSplit}
            onChange={toggleManualSplit}
            style={{ width: "auto", marginBottom: 0 }}
          />
          <span>Dividir de forma desigual</span>
        </label>

        {manualSplit &&
          participants.map((p) => (
            <div key={p.id} className="row">
              <span style={{ width: 100 }}>{p.name}</span>
              <input
                value={manualAmounts[p.id] || ""}
                onChange={(e) =>
                  setManualAmounts((prev) => ({
                    ...prev,
                    [p.id]: e.target.value,
                  }))
                }
                placeholder="0.00"
                inputMode="decimal"
              />
            </div>
          ))}

        {!manualSplit && (
          <p className="muted">
            Divide automaticamente em partes iguais entre todos os
            participantes.
          </p>
        )}

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Lançando..." : "Lançar gasto"}
        </button>
      </form>
    </div>
  );
}

function ExpensesCard({ expenses, participants }) {
  if (expenses.length === 0) return null;

  return (
    <div className="card">
      <strong>Gastos lançados</strong>
      {expenses.map((e) => (
        <div key={e.id} className="list-item">
          <span>
            {e.description}{" "}
            <span className="muted">
              (pago por {nameById(participants, e.paid_by_id)})
            </span>
          </span>
          <span>R$ {e.amount.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

function BalancesCard({ balances }) {
  return (
    <div className="card">
      <strong>Saldos</strong>
      {balances.map((b) => (
        <div key={b.participant_id} className="list-item">
          <span>{b.name}</span>
          <span className={b.balance >= 0 ? "positive" : "negative"}>
            {b.balance >= 0 ? "+" : ""}
            R$ {b.balance.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  );
}

function SettlementsCard({ settlements }) {
  return (
    <div className="card">
      <strong>Acerto final</strong>
      {settlements.length === 0 ? (
        <p className="muted">Ninguém deve nada — tudo certo! 🎉</p>
      ) : (
        settlements.map((s, idx) => (
          <div key={idx} className="list-item">
            <span>
              {s.from_name} → {s.to_name}
            </span>
            <span>R$ {s.amount.toFixed(2)}</span>
          </div>
        ))
      )}
    </div>
  );
}
