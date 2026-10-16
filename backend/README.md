# Stock Management — Backend

FastAPI + PostgreSQL, clean architecture:

- `src/stock/core/`: pure Python business rules (entities, use cases, ports)
- `src/stock/infrastructure/`: PostgreSQL repositories, password hashing, JWT
- `src/stock/api/`: FastAPI routers and schemas
- `tests/core/`: unit tests, one per core file (no database needed)
- `tests/integration/`: API tests against a real PostgreSQL database

All commands below are run from the `backend/` folder.

## 1. Install

Requires Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Database

Create a PostgreSQL user and database (default: user `stock`, password `stock`, database `stock`):

```bash
sudo -u postgres psql -c "CREATE USER stock WITH PASSWORD 'stock';"
sudo -u postgres psql -c "CREATE DATABASE stock OWNER stock;"
sudo -u postgres psql -c "CREATE DATABASE stock_test OWNER stock;"   # for integration tests
```

Or start only the database with Docker, from the project root: `docker compose up -d db`
(then create `stock_test` with `docker compose exec db createdb -U stock stock_test`).
This database listens on port **5433**, so use
`postgresql+psycopg://stock:stock@localhost:5433/stock` for `DATABASE_URL`
(and `.../stock_test` for `TEST_DATABASE_URL`).

## 3. Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://stock:stock@localhost:5432/stock` | Main database |
| `JWT_SECRET` | dev value | Secret used to sign tokens. **Set a long random value in production.** |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins (comma-separated) |
| `TEST_DATABASE_URL` | `postgresql+psycopg://stock:stock@localhost:5432/stock_test` | Database used by integration tests |

Example:

```bash
export DATABASE_URL=postgresql+psycopg://stock:stock@localhost:5432/stock
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
```

## 4. Run

```bash
alembic upgrade head                                          # create / update tables
python -m stock.seed alice secret STOCK_MANAGER               # create users
python -m stock.seed bob secret PURCHASING_MANAGER
uvicorn stock.api.main:app --reload                           # start the API
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs (use the **Authorize** button to log in)

## 5. Unit tests (core)

No database needed:

```bash
pytest tests/core                                                   # run core unit tests
pytest tests/core -v                                                # verbose, one line per test
pytest tests/core --cov=stock.core --cov-report=term-missing        # with coverage report
pytest tests/core/entities/test_product.py                          # a single file
pytest tests/core -k reserve                                        # tests whose name contains "reserve"
```

## 6. Integration tests

Need the `stock_test` database (it is migrated and emptied automatically):

```bash
pytest tests/integration
pytest                                                              # everything (core + integration)
```

## 7. Lint & format

```bash
ruff check .                     # lint
ruff check --fix .               # lint and auto-fix
ruff format .                    # format code
```

## 8. Database migrations

After changing `src/stock/infrastructure/models.py`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
alembic downgrade -1             # undo the last migration
```
