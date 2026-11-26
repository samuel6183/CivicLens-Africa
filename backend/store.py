import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
 id INTEGER PRIMARY KEY,
 country TEXT NOT NULL, category TEXT NOT NULL, title TEXT NOT NULL,
 publisher TEXT NOT NULL, url TEXT NOT NULL, published_date TEXT NOT NULL,
 summary TEXT NOT NULL, indicator TEXT NOT NULL DEFAULT '',
 period TEXT NOT NULL DEFAULT '', value REAL, unit TEXT NOT NULL DEFAULT '',
 retrieved_at TEXT NOT NULL,
 UNIQUE(country, url, indicator, period)
);
CREATE INDEX IF NOT EXISTS records_category ON records(country, category);
CREATE INDEX IF NOT EXISTS records_indicator ON records(country, indicator, period);
"""
FIELDS = ("country","category","title","publisher","url","published_date","summary",
          "indicator","period","value","unit","retrieved_at")

@contextmanager
def connect():
    path = Path(os.environ.get("CIVICLENS_DB", "data/civiclens.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(SCHEMA)
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def upsert(records):
    sql = ("INSERT INTO records (" + ",".join(FIELDS) + ") VALUES (" +
           ",".join("?" for _ in FIELDS) + ") ON CONFLICT(country,url,indicator,period) "
           "DO UPDATE SET " + ",".join(f"{f}=excluded.{f}" for f in FIELDS
           if f not in ("country","url","indicator","period")))
    with connect() as db:
        db.executemany(sql, [tuple(r[f] for f in FIELDS) for r in records])

def search(q="", country="", category="", limit=25, offset=0):
    conditions, params = [], []
    for key, val in (("country", country), ("category", category)):
        if val:
            conditions.append(f"{key} = ?")
            params.append(val)
    for word in q.split()[:12]:
        conditions.append("instr(lower(title || ' ' || summary || ' ' || publisher || ' ' || indicator || ' ' || period), lower(?)) > 0")
        params.append(word)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    with connect() as db:
        total = db.execute("SELECT count(*) FROM records" + where, params).fetchone()[0]
        rows = db.execute("SELECT * FROM records" + where +
            " ORDER BY published_date DESC, period DESC, id DESC LIMIT ? OFFSET ?",
            params + [limit, offset]).fetchall()
    return {"total":total,"records":[dict(r) for r in rows]}

def overview():
    with connect() as db:
        counts = [dict(r) for r in db.execute(
            "SELECT country,category,count(*) AS count FROM records GROUP BY country,category ORDER BY country,category")]
        latest = db.execute("SELECT max(retrieved_at) FROM records").fetchone()[0]
    return {"counts":counts,"last_retrieved":latest}

def series(country, indicator):
    with connect() as db:
        return [dict(r) for r in db.execute(
            "SELECT period,value,unit,url,publisher,retrieved_at FROM records WHERE country=? AND indicator=? AND value IS NOT NULL ORDER BY period",
            (country,indicator))]
