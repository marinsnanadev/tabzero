# Rachômetro — Frontend

SPA em React + Vite. Consome a API do backend (`../backend`).

## Rodando localmente

```bash
npm install
npm run dev
```

Por padrão aponta para `http://localhost:8000`. Para apontar para outra URL,
crie um `.env` com `VITE_API_URL=https://sua-api.com`.

## Telas

- `/` — criar sessão (nome + participantes)
- `/s/:slug` — dashboard: participantes, lançar gasto, saldos e acerto final

## Notas de segurança de dependências

`npm audit` aponta 2 vulnerabilidades moderadas em `react-router-dom`
(relacionadas a SSR e a `deserializeErrors`), cuja correção exige migrar
para a v7 — uma major com mudanças de API. Como este projeto é uma SPA
puramente client-side (sem SSR e sem uso de `deserializeErrors`), o risco
real é baixo; a migração fica registrada aqui como débito técnico
consciente, não como algo esquecido.
