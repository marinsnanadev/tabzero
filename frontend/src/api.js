const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Erro ${response.status} ao chamar ${path}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  createSession: (name, participantNames) =>
    request("/sessions", {
      method: "POST",
      body: JSON.stringify({ name, participant_names: participantNames }),
    }),

  getSession: (slug) => request(`/sessions/${slug}`),

  listParticipants: (slug) => request(`/sessions/${slug}/participants`),

  addParticipant: (slug, name) =>
    request(`/sessions/${slug}/participants`, {
      method: "POST",
      body: JSON.stringify({ name }),
    }),

  listExpenses: (slug) => request(`/sessions/${slug}/expenses`),

  createExpense: (slug, { description, amount, paidById, splits }) =>
    request(`/sessions/${slug}/expenses`, {
      method: "POST",
      body: JSON.stringify({
        description,
        amount,
        paid_by_id: paidById,
        splits: splits || [],
      }),
    }),

  getBalances: (slug) => request(`/sessions/${slug}/balances`),

  getSettlements: (slug) => request(`/sessions/${slug}/settlements`),
};
