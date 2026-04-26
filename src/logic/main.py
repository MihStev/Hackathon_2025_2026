"""
src/logic/main.py — Orchestrator / Scheduler

Pokreće simulaciju:
  - Svakih BANK_INTERVAL sekundi: generiše bank payload → upisuje u DB
  - Svakih INVOICE_INTERVAL sekundi: generiše invoice payload → upisuje u DB

Pokretanje:
    python -m src.logic.main
    ili
    python src/logic/main.py

Env varijable (ili .env fajl):
    BANK_INTERVAL=120        (sekunde, default 120 = 2 min)
    INVOICE_INTERVAL=300     (sekunde, default 300 = 5 min)
    BANK_TX_PER_RUN=3        (broj transakcija po runu)
    INVOICE_PER_RUN=2        (broj faktura po runu)
    LOG_LEVEL=INFO
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from src.mock_bank import generate_full_bank_payload
from src.invoice_models import generate_full_invoice_payload
from db.database import init_db, insert_bank_payload, insert_invoice_payload, get_recent_balance

# ─── Konfiguracija ────────────────────────────────────────────────────────────

BANK_INTERVAL    = int(os.getenv("BANK_INTERVAL", 120))
INVOICE_INTERVAL = int(os.getenv("INVOICE_INTERVAL", 300))
BANK_TX_PER_RUN  = int(os.getenv("BANK_TX_PER_RUN", 3))
INVOICE_PER_RUN  = int(os.getenv("INVOICE_PER_RUN", 2))
LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO").upper()
DATA_DIR         = ROOT / "data"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("nexus")


# ─── Job funkcije ─────────────────────────────────────────────────────────────

_tekuce_stanje: float | None = None


def run_bank_job() -> None:
    """Generiše i upisuje bank payload."""
    global _tekuce_stanje

    # Uzmi poslednje stanje iz baze ako ga nema u memoriji
    if _tekuce_stanje is None:
        poslednji = get_recent_balance()
        _tekuce_stanje = poslednji["stanje_ocekivano"] if poslednji else 150_000.0
        log.info(f"[BANKA] Početno stanje: {_tekuce_stanje:,.2f} RSD")

    payload = generate_full_bank_payload(
        current_balance=_tekuce_stanje,
        num_new_transactions=BANK_TX_PER_RUN,
    )

    rezultat = insert_bank_payload(payload)
    _tekuce_stanje = payload["novo_stanje"]

    # Sačuvaj JSON snapshot na disk (opciono, za debug)
    ts        = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snap_path = DATA_DIR / f"banka_{ts}.json"
    snap_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info(
        f"[BANKA] ✓ {rezultat['transakcije_upisane']} transakcija | "
        f"stanje: {_tekuce_stanje:,.2f} RSD | "
        f"→ {snap_path.name}"
    )


def run_invoice_job() -> None:
    """Generiše i upisuje invoice payload."""
    payload  = generate_full_invoice_payload(count=INVOICE_PER_RUN)
    rezultat = insert_invoice_payload(payload)

    ts        = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snap_path = DATA_DIR / f"fakture_{ts}.json"
    snap_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    log.info(
        f"[FAKTURE] ✓ {rezultat['fakture_upisane']} faktura | "
        f"ukupno: {payload['ukupnoFaktura']:,.2f} RSD | "
        f"→ {snap_path.name}"
    )


# ─── Scheduler ────────────────────────────────────────────────────────────────

def run_scheduler() -> None:
    """
    Jednostavan scheduler baziran na time.sleep.

    Za produkciju, zameni sa APScheduler ili Celery.
    """
    log.info("=" * 55)
    log.info("  Google Nexus — Simulator pokrenuto")
    log.info(f"  Bankovna transakcija: svakih {BANK_INTERVAL}s")
    log.info(f"  Fakture:              svakih {INVOICE_INTERVAL}s")
    log.info("  Ctrl+C za zaustavljanje")
    log.info("=" * 55)

    # Inicijalni run odmah pri pokretanju
    run_bank_job()
    run_invoice_job()

    bank_tajmer    = 0
    invoice_tajmer = 0
    TICK = 10  # sekundi

    try:
        while True:
            time.sleep(TICK)
            bank_tajmer    += TICK
            invoice_tajmer += TICK

            if bank_tajmer >= BANK_INTERVAL:
                run_bank_job()
                bank_tajmer = 0

            if invoice_tajmer >= INVOICE_INTERVAL:
                run_invoice_job()
                invoice_tajmer = 0

    except KeyboardInterrupt:
        log.info("\n[NEXUS] Simulator zaustavljen.")


# ─── Bulk seed (za testove) ───────────────────────────────────────────────────

def seed_database(num_bank_runs: int = 10, num_invoice_runs: int = 5) -> None:
    """
    Brzo popunjava bazu sa istorijskim podacima za testiranje.

    Args:
        num_bank_runs:    Broj bank run-ova (svaki ima BANK_TX_PER_RUN transakcija)
        num_invoice_runs: Broj invoice run-ova
    """
    log.info(f"[SEED] Popunjavam bazu: {num_bank_runs} bank + {num_invoice_runs} invoice run-ova...")

    global _tekuce_stanje
    _tekuce_stanje = 200_000.0  # Počni sa 200k za seed

    for i in range(num_bank_runs):
        run_bank_job()
        log.info(f"[SEED] Bank run {i+1}/{num_bank_runs}")

    for i in range(num_invoice_runs):
        run_invoice_job()
        log.info(f"[SEED] Invoice run {i+1}/{num_invoice_runs}")

    log.info("[SEED] ✓ Baza popunjena!")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    init_db()

    import argparse
    parser = argparse.ArgumentParser(description="Google Nexus Simulator")
    parser.add_argument("--seed", action="store_true", help="Seed bazu sa test podacima pa izađi")
    parser.add_argument("--bank-runs",    type=int, default=10)
    parser.add_argument("--invoice-runs", type=int, default=5)
    args = parser.parse_args()

    if args.seed:
        seed_database(num_bank_runs=args.bank_runs, num_invoice_runs=args.invoice_runs)
    else:
        run_scheduler()