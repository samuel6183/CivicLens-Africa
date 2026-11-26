# CivicLens Africa

Independent public intelligence platform for government, policy, procurement and economic insights. Kenya-first pilot.

## Run locally
Requires Python 3.10+.
```bash
python -m venv .venv
# Activate the virtual environment for your operating system.
pip install -r requirements.txt
python -m backend.ingest world-bank
python -m uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000 for the official-source directory and http://127.0.0.1:8000/records.html for the data explorer. API documentation is at /docs. The initial database is empty until ingestion succeeds. External requests require internet access. The source directory is not a live document search.

## Import public documents
Run `python -m backend.ingest documents --file your-metadata.json` with a JSON array of records containing country ("KE"), category, title, publisher, HTTPS url, published_date (YYYY-MM-DD or empty), and summary. Verify each source manually before import. Categories: Procurement, Public finance, Economy, Legislation.

## Tests
```bash
python -m unittest discover -s tests -v
```
Tests use mocked World Bank responses and a temporary database, never live data.

## Container
```bash
docker build -t civiclens .
docker volume create civiclens-data
docker run --rm -v civiclens-data:/data civiclens python -m backend.ingest world-bank
docker run --rm -p 8000:8000 -v civiclens-data:/data civiclens
```
Use a persistent writable volume and HTTPS in production. See docs/architecture.md for limitations and migration plans.

## Current scope
Searchable source directory, metadata search, public annual economic data ingestion (GDP growth, inflation and population), indicator tables, read-only API, tests and container configuration. No real-time procurement feeds, automated PDF collection, AI-generated analysis or production hosting yet. No government affiliation.
