#!/bin/sh
set -e

echo "Waiting for Postgres at ${DATABASE_URL}..."
python - <<'PY'
import os
import time

from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
engine = create_engine(url, pool_pre_ping=True)

for attempt in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Postgres is ready.")
        break
    except Exception as exc:
        print(f"Attempt {attempt + 1}/30: {exc}")
        time.sleep(1)
else:
    raise SystemExit("Postgres did not become ready in time")
PY

echo "Running migrations..."
alembic upgrade head

exec "$@"
