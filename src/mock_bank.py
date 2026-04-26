# -*- coding: utf-8 -*-
"""
src/mock_bank.py — Simulacija bankovnog računa (Open Banking JSON format)

Generiše realistične transakcije i stanje računa u srpskom finansijskom rečniku.
Dizajniran da lako bude zamenjen pravim Open Banking API-jem.
"""

import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import Optional

# ─── Podaci o računu ──────────────────────────────────────────────────────────

PODACI_RACUNA = {
    "identifikator": "c9c223a0-1234-5678-90ab-cdef12345678",
    "valuta":        "RSD",
    "vrstaRacuna":   "Tekući račun",
    "status":        "aktivan",
    "bic":           "DBSSDEFF",
    "iban":          "RS35160000000012345678",
    "imeTitulara":   "Stefan Branković",
    "proizvod":      "Tekući račun - Standard",
}

# ─── Šabloni transakcija ──────────────────────────────────────────────────────
# (kategorija, opis, min_iznos, max_iznos, vrsta)

SABLONI_TRANSAKCIJA = [
    ("plata",           "Plata — Moja Firma DOO",               150_000, 250_000, "odobrenje"),
    ("kirija",          "Kirija — stan Beograd",                  40_000,  80_000, "zaduzenje"),
    ("rezije",          "EPS — električna energija",               3_000,   8_000, "zaduzenje"),
    ("rezije",          "SBB — internet i kablovska",              2_500,   4_000, "zaduzenje"),
    ("rezije",          "Telekom — mobilna telefonija",            1_500,   3_000, "zaduzenje"),
    ("namirnice",       "Maxi — namirnice",                        1_200,   8_000, "zaduzenje"),
    ("namirnice",       "Lidl — namirnice",                          800,   5_000, "zaduzenje"),
    ("ugostiteljstvo",  "Restoran — poslovni ručak",                 500,   3_000, "zaduzenje"),
    ("gorivo",          "NIS Petrol — gorivo",                     2_000,   8_000, "zaduzenje"),
    ("prevoz",          "BusPlus — mesečna karta",                 3_800,   3_800, "zaduzenje"),
    ("zdravlje",        "Apoteka — lekovi",                          500,   4_000, "zaduzenje"),
    ("zabava",          "Netflix — mesečna pretplata",             1_099,   1_099, "zaduzenje"),
    ("zabava",          "Steam — digitalna kupovina",              1_000,   5_000, "zaduzenje"),
    ("honorar",         "Uplata — honorar za projekat",           20_000,  80_000, "odobrenje"),
    ("prenos_ulaz",     "Prenos sa štednog računa",               10_000,  50_000, "odobrenje"),
    ("prenos_izlaz",    "Prenos na štedni račun",                  5_000,  30_000, "zaduzenje"),
    ("porez",           "Poreska uprava — akontacija poreza",      3_000,  15_000, "zaduzenje"),
    ("osiguranje",      "Wiener Städtische — polisa osiguranja",   2_500,   5_000, "zaduzenje"),
    ("obrazovanje",     "Udemy — online kurs",                     1_500,   6_000, "zaduzenje"),
    ("kupovina",        "Online kupovina",                         1_000,  15_000, "zaduzenje"),
]


# ─── Pomoćne funkcije ─────────────────────────────────────────────────────────

def _sada_utc() -> datetime:
    return datetime.now(timezone.utc)


def _slucajni_iznos(min_val: float, max_val: float) -> float:
    iznos = random.uniform(min_val, max_val) * random.uniform(0.95, 1.05)
    return round(max(0.01, iznos), 2)


# ─── Generatori ───────────────────────────────────────────────────────────────

def generisi_transakciju(stanje_racuna: float, forsiraj_vrstu: Optional[str] = None) -> dict:
    """
    Generiše jednu bankovnu transakciju.

    Struktura odgovara Open Banking PSD2 standardu sa srpskim nazivima polja.
    """
    sablon = random.choice(SABLONI_TRANSAKCIJA)
    kategorija, opis, min_val, max_val, vrsta = sablon

    if forsiraj_vrstu:
        vrsta = forsiraj_vrstu

    iznos = _slucajni_iznos(min_val, max_val)

    if vrsta == "zaduzenje" and iznos > stanje_racuna * 0.9:
        iznos = round(stanje_racuna * random.uniform(0.05, 0.3), 2)

    ts = _sada_utc()
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "identifikatorTransakcije": str(uuid.uuid4()),
        "datumKnjizenja":           ts.date().isoformat(),
        "datumValute":              (ts.date() + timedelta(days=random.choice([0, 1]))).isoformat(),
        "iznos": {
            "valuta":   "RSD",
            "vrednost": iznos if vrsta == "odobrenje" else -iznos,
        },
        "nazivPoverioca": opis if vrsta == "zaduzenje" else None,
        "nazivDuznika":   opis if vrsta == "odobrenje" else None,
        "svrhaPlacanja":  opis,
        "kodTransakcije": "ODO" if vrsta == "odobrenje" else "ZAD",
        "kategorija":     kategorija,
        "interniKod":     f"{'ODO' if vrsta == 'odobrenje' else 'ZAD'}{random.randint(100,999)}",
    }


def generisi_stanje_racuna(pocetno_stanje: Optional[float] = None, broj_transakcija: int = 0) -> dict:
    """
    Generiše snimak stanja računa (balances endpoint).

    Polja:
      vrstaStanja     → tip salda (ocekivano / raspolozivo)
      iznos.vrednost  → iznos u RSD
      datumPromene    → timestamp poslednje promene
    """
    if pocetno_stanje is None:
        pocetno_stanje = round(random.uniform(50_000, 500_000), 2)

    rezervisano        = round(random.uniform(0, min(15_000, pocetno_stanje * 0.1)), 2)
    raspolozivo_stanje = round(pocetno_stanje - rezervisano, 2)

    ts     = _sada_utc()
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    id_r   = PODACI_RACUNA["identifikator"]

    return {
        "podaci": {
            "racun": PODACI_RACUNA,
            "stanja": [
                {
                    "vrstaStanja":     "ocekivano",
                    "iznos":           {"valuta": "RSD", "vrednost": pocetno_stanje},
                    "datumPromene":    ts_str,
                    "referentniDatum": ts.date().isoformat(),
                },
                {
                    "vrstaStanja":  "raspolozivo",
                    "iznos":        {"valuta": "RSD", "vrednost": raspolozivo_stanje},
                    "datumPromene": ts_str,
                },
            ],
        },
        "veze": {
            "ovaj":  {"putanja": f"/v1/racuni/{id_r}/stanja"},
            "racun": {"putanja": f"/v1/racuni/{id_r}"},
        },
        "meta": {
            "ukupnoRezultata":         2,
            "vremenskaOznaka":         ts_str,
            "brojTransakcijaUPeriodu": broj_transakcija,
        },
    }


def generisi_batch_transakcija(tekuce_stanje: float, broj: int = 5) -> tuple[list[dict], float]:
    """Generiše N transakcija i vraća listu + novo stanje računa."""
    transakcije = []
    stanje = tekuce_stanje
    for _ in range(broj):
        tx = generisi_transakciju(stanje)
        transakcije.append(tx)
        stanje += tx["iznos"]["vrednost"]
        stanje  = max(0.0, round(stanje, 2))
    return transakcije, stanje


def generate_full_bank_payload(
    current_balance: Optional[float] = None,
    num_new_transactions: int = 3,
) -> dict:
    """
    Glavni entry point — generiše kompletan bank payload spreman za bazu.

    Poziva se iz ingestion servisa svakih N minuta.

    Vraća:
        {
            "snimak":      <stanje računa>,
            "transakcije": [<lista transakcija>],
            "novo_stanje": float,
        }
    """
    if current_balance is None:
        current_balance = round(random.uniform(100_000, 300_000), 2)

    transakcije, novo_stanje = generisi_batch_transakcija(current_balance, num_new_transactions)
    snimak = generisi_stanje_racuna(pocetno_stanje=novo_stanje, broj_transakcija=num_new_transactions)

    return {
        "snimak":      snimak,
        "transakcije": transakcije,
        "novo_stanje": novo_stanje,
    }


if __name__ == "__main__":
    import json
    print("=== Snimak bankovnog računa ===")
    payload = generate_full_bank_payload(current_balance=150_000.50, num_new_transactions=3)
    print(json.dumps(payload, indent=2, ensure_ascii=False))