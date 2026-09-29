import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function CreateSessionPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [participantsText, setParticipantsText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const participantNames = participantsText
      .split(",")
      .map((n) => n.trim())
      .filter(Boolean);

    if (!name.trim()) {
      setError("Dê um nome para a sessão (ex: Viagem praia 2026).");
      return;
    }

    setLoading(true);
    try {
      const session = await api.createSession(name.trim(), participantNames);
      navigate(`/s/${session.slug}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1>Tabzero</h1>
      <p className="muted">
        Crie uma sessão, lance os gastos do grupo e receba o menor número de
        transferências para todo mundo ficar quite.
      </p>

      <form className="card" onSubmit={handleSubmit}>
        <label>Nome da sessão</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ex: Viagem praia 2026"
        />

        <label>Participantes (separados por vírgula)</label>
        <input
          value={participantsText}
          onChange={(e) => setParticipantsText(e.target.value)}
          placeholder="Ana, Bruno, Carla"
        />

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Criando..." : "Criar sessão"}
        </button>
      </form>
    </>
  );
}
