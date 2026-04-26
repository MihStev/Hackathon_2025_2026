"""
src/ingestion/invoice_service.py — Invoice ingestion service

Odgovoran za:
  - Pozivanje invoice_models generatora (ili pravog eFaktura API-ja)
  - Validaciju JSON-a
  - Upis u bazu

Zamena za pravi API: samo promeni fetch_invoices() funkciju.
"""

import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.invoice_models import generate_full_invoice_payload
from db.database import insert_invoice_payload

log = logging.getLogger("nexus.fakture")


def fetch_invoices(broj: int = 2) -> dict:
    """
    Dohvata fakture.

    MOCK: Generiše simulirane fakture.
    PRODUKCIJA: Zameni sa eFaktura API pozivom:

        import httpx
        response = httpx.get(
            "https://efaktura.mfin.gov.rs/api/publicApi/purchase-invoice/ids",
            headers={"ApiKey": EFAKTURA_API_KEY}
        )
        # ...parsiranje eFaktura XML/JSON formata
    """
    log.debug(f"[FAKTURE] Dohvatam {broj} faktura")
    return generate_full_invoice_payload(count=broj)


def process_invoice_run(broj: int = 2) -> dict:
    """
    Kompletan invoice run: dohvati → validiraj → upiši.

    Vraća:
        {
            "fakture_upisane": int,
            "ukupnoFaktura":   float,
        }
    """
    payload  = fetch_invoices(broj)
    rezultat = insert_invoice_payload(payload)

    log.info(
        f"[FAKTURE] Run završen: {rezultat['fakture_upisane']} faktura | "
        f"ukupno: {payload['ukupnoFaktura']:,.2f} RSD"
    )
    return {**rezultat, "ukupnoFaktura": payload["ukupnoFaktura"]}