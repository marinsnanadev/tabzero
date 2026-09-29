# Tabzero

Divisor de contas em grupo: crie uma sessão, lance os gastos e receba uma lista
enxuta de transferências para todo mundo ficar com a conta **zerada**.

Sem cadastro e sem login: cada sessão tem um link único e não adivinhável
(ex: `viagem-praia-a1b2c3`) que você compartilha com o grupo.

## Como funciona

1. Crie uma sessão com o nome do evento e os participantes.
2. Lance os gastos: quem pagou, quanto foi, e como dividir (partes iguais
   automaticamente ou valores manuais por pessoa).
3. Veja o saldo de cada participante (positivo = a receber, negativo = a pagar).
4. Veja o acerto final: quem paga quanto para quem.

### Algoritmo de acerto

O saldo de cada pessoa é `total pago - total devido`. Para o acerto, um
algoritmo guloso casa repetidamente quem mais deve com quem mais tem a
receber, em O(n log n). Isso zera todos os saldos com **no máximo n-1
transferências** e costuma chegar bem perto do mínimo, mas não garante o
mínimo absoluto (esse problema é NP-difícil no caso geral).

## Stack

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + Vite + React Router
- Testes: pytest (13 testes: lógica de cálculo e rotas da API)

## Estrutura

```
backend/
  app/
    main.py           # app FastAPI, CORS, /health
    database.py       # engine e sessão SQLAlchemy
    models.py         # Session, Participant, Expense, ExpenseSplit
    schemas.py        # validação de entrada/saída (Pydantic)
    calculations.py   # saldos e simplificação de dívidas (lógica pura)
    utils.py          # geração de slug único
    routers/sessions.py
  tests/
frontend/
  src/
    api.js            # cliente da API
    pages/            # CreateSessionPage, SessionPage
```

## Rodando o backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000` e a documentação interativa fica em
`http://localhost:8000/docs`. O banco `tabzero.db` é criado
automaticamente na primeira execução.

## Rodando o frontend

```bash
cd frontend
npm install
npm run dev
```

O app abre em `http://localhost:5173` e aponta por padrão para
`http://localhost:8000`. Para usar outra URL de API, crie um arquivo `.env`
em `frontend/` com `VITE_API_URL=https://sua-api.com`.

## Rodando os testes

```bash
cd backend
python -m pytest tests/ -v
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Verificação de saúde |
| POST | `/sessions` | Cria sessão (nome + participantes opcionais) |
| GET | `/sessions/{slug}` | Dados da sessão |
| POST | `/sessions/{slug}/participants` | Adiciona participante |
| GET | `/sessions/{slug}/participants` | Lista participantes |
| POST | `/sessions/{slug}/expenses` | Lança gasto (divisão igual ou manual) |
| GET | `/sessions/{slug}/expenses` | Lista gastos |
| GET | `/sessions/{slug}/balances` | Saldo líquido de cada participante |
| GET | `/sessions/{slug}/settlements` | Transferências para quitar o grupo |

Na divisão manual, a soma dos valores por pessoa precisa bater com o valor do
gasto (tolerância de 2 centavos); caso contrário a API responde 400.

## Notas

- Qualquer pessoa com o link da sessão pode ver e editar os dados dela. Não
  há autenticação por design; não use para informações sensíveis.
- `npm audit` aponta 2 vulnerabilidades moderadas no `react-router-dom`
  (relacionadas a SSR), cuja correção exige migrar para a v7. Como o
  frontend é uma SPA sem SSR, o risco real é baixo; a migração fica como
  débito técnico consciente.

## Próximos passos possíveis

- Deploy (backend + frontend) e troca do SQLite por PostgreSQL
- Geração de PIX copia-e-cola no acerto final
- Migração do `react-router-dom` para a v7