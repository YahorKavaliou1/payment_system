# Payment System

FastAPI service that handles bank payment webhooks, records payments, and activates subscriptions.

## Requirements

- Python 3.13+
- Docker & Docker Compose
- `psql` (optional, for manual DB access)

## Create the Python environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If your default package index cannot resolve packages:

```bash
pip install --index-url https://pypi.org/simple -r requirements.txt
```

Create a local env file:

```bash
cp .env.example .env
```

Default connection string (host → Docker Postgres on localhost):

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/payment_system
```

## Start Docker from scratch

Build and start **Postgres + the app**:

```bash
docker compose down -v   # optional: wipe previous containers/volumes
docker compose up -d --build
```

What this does:

1. Starts Postgres 16 (`payment_system_db`) on port `5432`
2. Builds the app image
3. Waits until Postgres is healthy
4. Runs `alembic upgrade head`
5. Starts the API on port `8000`

Check status:

```bash
docker compose ps
curl http://localhost:8000/health
```

Stop everything:

```bash
docker compose down
```

Remove containers **and** DB data:

```bash
docker compose down -v
```

### Postgres only

If you want to run the API on the host and only use Docker for the database:

```bash
docker compose up -d db
```

## Run the app locally

With Postgres running (e.g. `docker compose up -d db`) and the venv activated:

```bash
source .venv/bin/activate
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

Example webhook:

```bash
curl -X POST http://localhost:8000/webhook/payment \
  -H 'Content-Type: application/json' \
  -d '{"payment_id":"abc-123","user_id":1,"amount":4900,"status":"CONFIRMED"}'
```

> `user_id` must exist in `users` first.

## Connect to the local DB

Docker exposes Postgres on **localhost:5432**.

| Setting  | Value            |
|----------|------------------|
| Host     | `localhost`      |
| Port     | `5432`           |
| User     | `postgres`       |
| Password | `postgres`       |
| Database | `payment_system` |

### psql (host)

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d payment_system
```

Useful commands:

```sql
\dt
SELECT * FROM users;
SELECT * FROM payments;
SELECT * FROM subscriptions;
\q
```

One-shot:

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d payment_system -c '\dt'
```

### psql (inside the container)

```bash
docker compose exec db psql -U postgres -d payment_system
```

### App connection strings

| Where the app runs      | `DATABASE_URL` |
|-------------------------|----------------|
| Host / local uvicorn    | `postgresql+psycopg2://postgres:postgres@localhost:5432/payment_system` |
| Inside docker-compose   | `postgresql+psycopg2://postgres:postgres@db:5432/payment_system` (set in `docker-compose.yml`) |

## Tests

```bash
source .venv/bin/activate
pytest -q
```

## Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```
