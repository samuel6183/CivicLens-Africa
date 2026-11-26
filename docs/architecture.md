# Architecture and limitations

Browser -> FastAPI (read-only API) -> SQLite indexed metadata and annual indicator observations.
Operators run ingestion separately. World Bank API ingestion validates country, year and finite numeric values, skips missing observations, and upserts by source/indicator/period. JSON document import accepts operator-curated public metadata; it does not crawl websites or verify provenance automatically.

SQLite is a deliberate low-cost single-instance pilot choice. Move to PostgreSQL before multi-instance deployment or sustained concurrent writes. Keep database on a persistent volume and back it up. No secrets are required for the World Bank public API.

Before public deployment: verify source URLs and access terms; run tests; inspect imported data against publisher records; configure HTTPS, rate limiting, backups and monitoring. No person-level political profiles, personal data, or inferred voter attributes are part of the design.

Automated procurement/budget scraping, full-text PDF indexing, and AI summaries are not implemented. Future ingestion should retain publication date, source URL, retrieval date and document hashes, with retries and explicit freshness status. AI summaries should cite underlying documents and be labeled as generated.
