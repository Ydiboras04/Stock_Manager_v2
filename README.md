# Stock Management

Stock management app based on `BPMN_Diagramme_GestionStock.drawio`
(entry, exit and replenishment processes).

- **backend/**: Python, clean architecture, FastAPI + PostgreSQL
- **frontend/**: React + TypeScript (Vite)
- **.github/workflows/ci.yml**: CI/CD with GitHub Actions

## Architecture

```
backend/src/stock/
├── core/             # Pure Python (stdlib only): business rules
│   ├── entities/     # Product, CustomerOrder, PurchaseRequest, SupplierOrder, Notification
│   ├── use_cases/    # products, exit, entry, replenishment, notifications
│   ├── ports.py      # Repository interfaces
│   ├── roles.py      # Stock manager / purchasing manager
│   └── errors.py
├── infrastructure/   # PostgreSQL (SQLAlchemy) repositories, password hashing, JWT
└── api/              # FastAPI routers, Pydantic schemas, auth dependencies
```

Dependencies only point inward: `api → infrastructure → core`.
`tests/core/test_core_is_pure.py` fails if the core imports anything outside the stdlib.

Each core file has its own unit test in `backend/tests/core/` (same path, `test_` prefix).
These tests use in-memory repositories (`tests/core/conftest.py`), so they don't need a database.

### Business flows

| BPMN process | Flow | Role |
|---|---|---|
| Exit | Customer order → `RESERVED` → `PREPARED` → `SHIPPED`. If the stock is too low, the order is `REJECTED` automatically, both roles get a notification and the missing quantity is ordered | Stock manager |
| Replenishment | Purchase request created automatically when available ≤ Qmin, or for the missing quantity of a rejected order (added to the product's `PENDING` request if there is one), or manually → `VALIDATED` / `REJECTED` → supplier order | Purchasing manager |
| Supplier (external) | Supplier order `ORDERED` → `SHIPPED` → `RECEIVED`, updated manually | Purchasing manager |
| Entry | Received order → conformity check → `ACCEPTED` (stock updated, accounting validation pending) or `REJECTED` (non-conformity report) | Stock manager |

Both roles can view everything.

## Run with Docker

```bash
docker compose up --build
docker compose exec backend python -m stock.seed alice secret STOCK_MANAGER
docker compose exec backend python -m stock.seed bob secret PURCHASING_MANAGER
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## Local development

Backend (needs a running PostgreSQL; `DATABASE_URL` defaults to
`postgresql+psycopg://stock:stock@localhost:5432/stock`):

```bash
cd backend
uv sync --extra dev            # or: python -m venv .venv && .venv/bin/pip install -e '.[dev]'
uv run alembic upgrade head
uv run python -m stock.seed alice secret STOCK_MANAGER
uv run uvicorn stock.api.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev                    # VITE_API_URL defaults to http://localhost:8000
```

## Tests

```bash
cd backend
uv run pytest tests/core       # core unit tests, no database needed
TEST_DATABASE_URL=postgresql+psycopg://stock:stock@localhost:5432/stock_test \
  uv run pytest tests/integration
uv run ruff check . && uv run ruff format --check .
```

After changing `infrastructure/models.py`, create a migration with
`uv run alembic revision --autogenerate -m "description"`.

## CI/CD

GitHub Actions, in `.github/workflows/ci.yml`. It runs on every pull request and every push to `main`:

1. **backend**: install `backend/requirements.txt`, ruff, core unit tests (100% coverage required),
   integration tests against a PostgreSQL service.
2. **frontend**: `npm ci`, lint, build (includes the TypeScript check).
3. **docker**: builds the backend and frontend images. On pushes to `main` only, they are
   published to GitHub Container Registry as `ghcr.io/<owner>/<repo>-backend` and `-frontend`,
   tagged `latest` and with the commit SHA.

The deploy step is still to be added once a hosting target is chosen.

Set `JWT_SECRET` to a long random value in production.
