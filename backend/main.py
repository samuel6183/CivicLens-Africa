from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from backend.store import search, overview, series, connect

app = FastAPI(title="CivicLens Africa", version="0.1.0")

@app.get("/api/health")
def health():
    with connect() as db:
        db.execute("SELECT 1")
    return {"status":"ok"}

@app.get("/api/search")
def records(q: str=Query("",max_length=200), country: str=Query("KE",max_length=2),
            category: str=Query("",max_length=40), limit: int=Query(25,ge=1,le=100),
            offset: int=Query(0,ge=0,le=100000)):
    return search(q,country,category,limit,offset)

@app.get("/api/overview")
def stats():
    return overview()

@app.get("/api/series")
def indicator(indicator: str=Query(...,min_length=1,max_length=80),country: str=Query("KE",max_length=2)):
    return {"indicator":indicator,"country":country,"observations":series(country,indicator)}

app.mount("/", StaticFiles(directory=Path(__file__).resolve().parents[1]/"frontend",html=True),name="frontend")
