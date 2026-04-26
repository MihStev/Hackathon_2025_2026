"""
src/ingestion/bank_service.py — Bank ingestion service

Odgovoran za:
  - Pozivanje mock_bank generatora (ili pravog Open Banking API-ja u budućnosti)
  - Validaciju JSON-a pre upisa
  - Upis u bazu

Zamena za pravi API: samo promeni fetch_bank_data() funkciju.
"""

import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.mock_bank import generate_full_bank_payload
from db.database import insert_bank_payload, get_recent_balance

log = logging.getLogger("nexus.banka")


def fetch_bank_data(tekuce_stanje: float = None, broj_transakcija: int = 3) -> dict:
    """
    Dohvata podatke sa bankovnog računa.

    MOCK: Poziva mock_bank generator.
    PRODUKCIJA: Zameni sa HTTP pozivom prema Open Banking API-ju:

        import httpx
        response = httpx.get(
            "https://api.banka.rs/v1/racuni/{id_racuna}/stanja",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        return response.json()
    """
    log.debug(f"[BANKA] Dohvatam podatke (tekuće stanje={tekuce_stanje})")
    return generate_full_bank_payload(
        current_balance=tekuce_stanje,
        num_new_transactions=broj_transakcija,
    )


def process_bank_run(broj_transakcija: int = 3) -> dict:
    """
    Kompletan bank run: dohvati → validiraj → upiši.

    Vraća:
        {
            "snimci_upisani":      int,
            "transakcije_upisane": int,
            "novo_stanje":         float,
        }
    """
    # Uzmi poslednje stanje iz baze
    poslednji = get_recent_balance()
    tekuce_stanje = poslednji["stanje_ocekivano"] if poslednji else None

    # Dohvati podatke
    payload = fetch_bank_data(tekuce_stanje, broj_transakcija)

    # Upiši u bazu
    rezultat = insert_bank_payload(payload)

    log.info(
        f"[BANKA] Run završen: {rezultat['transakcije_upisane']} transakcija | "
        f"novo stanje: {payload['novo_stanje']:,.2f} RSD"
    )
    return {**rezultat, "novo_stanje": payload["novo_stanje"]}