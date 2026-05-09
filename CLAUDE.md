# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FinAssist AI** is a hackathon MVP for a financial management dashboard targeting Serbian companies. It consolidates bank accounts, invoices, employees, and fixed expenses into a single Streamlit UI with an AI chat assistant. The app runs in Serbian with RSD currency.

## Commands

```bash
# Run the app
streamlit run app.py

# Run invoice subsystem tests (from novo/ directory)
cd novo && python test_azuriranje.py

# Use the invoice CLI helper
cd novo && python helper.py ucitaj 1.json     # load invoice
cd novo && python helper.py sve               # list all invoices
cd novo && python helper.py stats             # analytics
```

Before installing any package, ask for permission and add it to `requirements.txt`.

## Architecture

The app is split into two subsystems:

**Root-level (main dashboard)** — uses `sqlite3` directly:
- `mock_apis.py` — mock Berlin Group NextGenPSD2 bank/invoice data (Serbian company names, RSD, Jan–Mar 2025 transactions)
- `db_manager.py` — SQLite operations for `Zaposleni` (employees) and `Fiksni_Troskovi` (fixed expenses)
- `ai_agent.py` — keyword-based router (no live LLM calls yet); entry point is `odgovori(upit: str) -> str`; routes: `neplacene_fakture`, `fakture`, `fiksni_troskovi`, `zaposleni`, `transakcije`, `racun`, `opste`
- `app.py` — Streamlit dashboard with metrics, cash-flow bar chart, transaction/invoice tabs, and chat UI

**`novo/` subsystem** — newer invoice management using SQLAlchemy:
- Tables: `fakture`, `stavke_fakture`, `bankovni_racuni`, `stanja_racuna`
- JSON format: UBL-2.1-Simplified; UPSERT logic deletes old line items before re-inserting
- Has its own `.venv/` and `database.db`

## Key Conventions

- **KISS:** No complex classes or abstractions — plain functions only. This is a hackathon.
- **Mock data:** Use Serbian company names, RSD currency, realistic amounts when adding test data.
- **Secrets:** All API keys via `.env` + `python-dotenv`. Never hardcode.
- **LLM:** Vertex AI (`google-cloud-vertexai`) is wired in but currently returns mock responses. Real calls go through `ai_agent.py`.
- **Language:** All UI text, comments, and variable names are in Serbian (mixed Cyrillic/Latin).
