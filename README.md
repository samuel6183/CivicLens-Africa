# CivicLens Africa

Independent public intelligence platform for government, policy, procurement and economic insights in Africa.

## Kenya pilot
The current prototype is a searchable directory of six official public-information sources. Search matches source names, descriptions and categories; it does not search underlying documents or live records. No government affiliation is implied.

## Run locally
Open `frontend/index.html` in a browser, or run `python -m http.server 8000 --directory frontend` from the repository root and visit http://localhost:8000. No dependencies required.

## Manual acceptance checks
- Initial view shows six sources.
- Searching `inflation` shows KNBS.
- Selecting Procurement shows the procurement portal when the search field is empty.
- A nonsense query shows an empty-state message.
- Source links open official websites; verify availability before relying on them.

## Roadmap
1. Verify source URLs, access terms, and document availability.
2. Build ingestion for public budgets, procurement notices, and economic releases, preserving source URL, publisher, dates, country, category, and retrieval timestamp.
3. Normalize and deduplicate records; add validation and provenance checks.
4. Implement a backend search API and persistent database, then connect the frontend.
5. Add aggregate analytics, freshness indicators, automated tests, and deployment.

Use public institutional data only; avoid collecting unnecessary personal data. Distinguish missing data from zero, and never represent sample records as official statistics.
