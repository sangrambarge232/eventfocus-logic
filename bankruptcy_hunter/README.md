# BankruptcyHunter

BankruptcyHunter is a production-minded starter project for multilingual
bankruptcy and financial distress discovery. It includes a FastAPI backend,
Streamlit analyst dashboard, SQLite local storage, PostgreSQL-ready settings,
RSS and manual URL ingestion, article extraction, keyword matching,
translation/classification/scoring abstractions, deduplication, exports, and
structured logging.

## Project layout

```text
bankruptcy_hunter/
├── app/
│   ├── main.py                 # FastAPI application factory and startup hook
│   ├── api/                    # HTTP routes and request/response schemas
│   ├── collectors/             # RSS, manual URL, and search provider adapters
│   ├── extraction/             # Article download and readable text extraction
│   ├── ml/                     # Keywords, model registry, translation, classifier
│   ├── scoring/                # Priority scoring engine
│   ├── dedup/                  # Fingerprint deduplication
│   ├── config/                 # Environment-backed settings
│   ├── db/                     # SQLite local schema and connection helpers
│   ├── exports/                # CSV and Excel export writers
│   └── utils/                  # Logging, errors, and text normalization
├── dashboard/                  # Streamlit dashboard
├── tests/                      # Starter smoke tests
├── data/                       # Local data and Hugging Face model registry
├── logs/                       # Runtime logs (generated logs are ignored)
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── run_local.py
```

## Requirements

- Python 3.11 or newer
- SQLite for local development (included with Python)
- PostgreSQL for production deployments when `DATABASE_URL` is changed and a
  SQLAlchemy-backed persistence layer is enabled

## Setup

```bash
cd bankruptcy_hunter
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The default `.env.example` configuration uses SQLite at
`data/bankruptcy_hunter.db`. External search and translation providers are not
enabled by default; add API keys only when implementing live provider adapters.

## Run the FastAPI backend

```bash
python run_local.py
```

Open <http://127.0.0.1:8000/docs> for the interactive OpenAPI UI. Useful
starter endpoints include:

- `GET /api/health`
- `POST /api/analyze-text`
- `POST /api/ingest/manual`

## Run the Streamlit dashboard

```bash
PYTHONPATH=. streamlit run dashboard/streamlit_app.py
```

The dashboard currently supports direct text analysis and documents the external
provider setup points.

## Run tests and import checks

```bash
PYTHONPATH=. pytest
python -m compileall app dashboard tests
```


## EventWatch input files

Place user-provided EventWatch files in `data/input/` before running workflows
that depend on historical rules or examples:

- `eventwatch_rulebook(4).py` (required; loads `EVENTWATCH_RULEBOOK` and keeps only Bankruptcy/Financial Distress guidance)
- `eventwatch_industries(1).csv` (required; the only allowed dashboard industry universe)
- `bankruptcy_events_100_full.csv` (required; internal MUST Report / DO NOT Report training and filtering examples)
- `EventWatch Notifications Tracker (2021 - onwards) - Copy (3)(1).xlsx` (optional internal historical samples; never shown on dashboard)
- `2025 - EventWatch Complaints (3)(1).xlsx` (optional internal missed/delayed event samples; never shown on dashboard)

Use `src.file_loader` helper functions to load these files. Required files raise
clear `FileLoaderError` messages when missing; optional tracker files return an
empty sample and log a warning.

## Configuration

Settings are loaded from environment variables in `app/config/settings.py`.
Important variables:

| Variable | Purpose | Local default |
| --- | --- | --- |
| `DATABASE_URL` | SQLite or PostgreSQL DSN | `sqlite:///data/bankruptcy_hunter.db` |
| `HF_MODEL_REGISTRY` | Hugging Face model registry JSON | `data/model_registry.json` |
| `EXPORT_DIR` | CSV/XLSX export directory | `data/exports` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `USER_AGENT` | HTTP user agent for ingestion/extraction | `BankruptcyHunter/0.1 (+local-dev)` |

## Architecture notes

- **Search providers:** implement the `SearchProvider` protocol and register
  adapters with `SearchProviderRegistry`.
- **RSS ingestion:** `RssCollector` parses RSS and Atom feeds into normalized
  `CollectedItem` objects.
- **Manual ingestion:** `ManualUrlCollector` validates analyst-supplied HTTP(S)
  URLs.
- **Extraction:** `ArticleExtractor` provides a standard-library HTML extractor
  suitable for local smoke tests; production can swap in trafilatura,
  newspaper3k, or a hosted extraction service.
- **Multilingual matching:** `KeywordMatcher` includes starter bankruptcy and
  distress terms in English, Spanish, French, German, and Portuguese.
- **Translation:** `TranslationLayer` is a stable facade with a pass-through
  local implementation until translation credentials or local models are chosen.
- **Classification:** `RuleBasedClassifier` provides deterministic starter
  behavior; Hugging Face model metadata is managed by `ModelRegistry`.
- **Scoring:** `ScoringEngine` converts classification evidence into a 0-100
  priority score.
- **Deduplication:** `FingerprintDeduplicator` hashes normalized URL and content
  fingerprints.
- **Exports:** `ExportWriter` writes CSV and XLSX files for analysts.

## Production TODOs requiring external credentials

- Add and test live search provider adapters after obtaining search API keys.
- Select and benchmark translation and classification models or APIs.
- Replace the starter SQLite connection module with SQLAlchemy sessions for
  PostgreSQL migrations, pooling, and production observability.
