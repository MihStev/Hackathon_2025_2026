"""
src/invoice_models.py — Simulacija eFaktura (UBL-2.1 Simplified format)

Generiše realistične fakture između srpskih firmi.
Dizajniran da lako bude zamenjen pravim eFaktura API-jem.
"""

import uuid
import random
from datetime import datetime, timedelta, timezone
from typing import Optional


# ─── Katalog firmi ────────────────────────────────────────────────────────────

PRODAVCI = [
    {"naziv": "Mnogo Jaka Firma DOO",       "pib": "101234567", "mb": "12345678"},
    {"naziv": "TechSolutions Serbia DOO",   "pib": "102345678", "mb": "23456789"},
    {"naziv": "Digital Agency NS DOO",      "pib": "103456789", "mb": "34567890"},
    {"naziv": "Consulting Pro DOO",         "pib": "104567890", "mb": "45678901"},
]

KUPCI = [
    {"naziv": "Kupac Partner DOO",          "pib": "107654321", "mb": "87654321"},
    {"naziv": "Republika Srbija - MUP",     "pib": "108765432", "mb": "11111111"},
    {"naziv": "NIS Petrol AD",              "pib": "109876543", "mb": "22222222"},
    {"naziv": "Telekom Srbija AD",          "pib": "110987654", "mb": "33333333"},
    {"naziv": "Banca Intesa AD",            "pib": "111098765", "mb": "44444444"},
    {"naziv": "Startup Hub Belgrade",       "pib": "112109876", "mb": "55555555"},
]

# Katalog usluga i dobara sa realnim cenama (bez PDV-a)
# (opis, min_cena, max_cena, jedinica_mere, kategorija)
KATALOG_USLUGA = [
    ("Razvoj AI Modela",                    30_000,  150_000, "usluga",  "IT"),
    ("Web razvoj - Frontend",               20_000,   80_000, "usluga",  "IT"),
    ("Web razvoj - Backend",                25_000,  100_000, "usluga",  "IT"),
    ("Konsultantske usluge",                10_000,   60_000, "sat",     "Konsalting"),
    ("Izrada poslovnog plana",              15_000,   50_000, "usluga",  "Konsalting"),
    ("Marketinška kampanja",                20_000,   80_000, "usluga",  "Marketing"),
    ("SEO optimizacija",                     8_000,   30_000, "mesec",   "Marketing"),
    ("Grafički dizajn - Logo",               5_000,   20_000, "usluga",  "Dizajn"),
    ("Fotografske usluge",                   8_000,   30_000, "usluga",  "Mediji"),
    ("Serverski hosting",                    3_000,   15_000, "mesec",   "IT"),
    ("Licenca softvera",                     5_000,   40_000, "komad",   "IT"),
    ("Obuka zaposlenih",                    10_000,   40_000, "dan",     "Edukacija"),
    ("Prevođenje dokumenata",                2_000,   10_000, "strana",  "Usluge"),
    ("Računovodstvene usluge",               8_000,   25_000, "mesec",   "Finansije"),
    ("Pravne usluge",                       15_000,   60_000, "sat",     "Pravo"),
    ("Laptop Dell XPS 15",                  90_000,  120_000, "komad",   "Oprema"),
    ("Monitor LG 27 inch",                  30_000,   50_000, "komad",   "Oprema"),
    ("Uredski materijal",                    1_000,    5_000, "usluga",  "Kancelarija"),
]

# PDV stope u Srbiji
STOPE_PDV = {
    "opsta":    20.0,   # Opšta stopa
    "snizena":  10.0,   # Smanjena stopa (hrana, lekovi...)
    "nulta":     0.0,   # Izvoz, itd.
}

# Serijski broj fakture za ovu sesiju
_brojac_faktura = [1]


# ─── Generatori ───────────────────────────────────────────────────────────────

def _sada_utc() -> datetime:
    return datetime.now(timezone.utc)


def _sledeci_broj_fakture(prefiks: str = "F") -> str:
    """Generiše serijski broj fakture."""
    godina = _sada_utc().year
    redni = _brojac_faktura[0]
    _brojac_faktura[0] += 1
    return f"{prefiks}-{godina}-{redni:04d}"


def generisi_stavku_fakture(
    filter_kategorije: Optional[str] = None,
    kolicina_override: Optional[float] = None,
) -> dict:
    """
    Generiše jednu stavku fakture.

    Polja:
      opis            → naziv usluge ili dobra
      kategorija      → kategorija stavke
      jedinicaMere    → sat / komad / mesec / usluga...
      kolicina        → broj jedinica
      cenaPoJedinici  → cena bez PDV-a
      stopaPDV        → procenat PDV-a
      iznosOsnove     → cena × količina (bez PDV-a)
      iznosPDV        → iznos PDV-a
      ukupanIznos     → iznosOsnove + iznosPDV
    """
    katalog = KATALOG_USLUGA
    if filter_kategorije:
        katalog = [s for s in KATALOG_USLUGA if s[4] == filter_kategorije] or KATALOG_USLUGA

    usluga = random.choice(katalog)
    opis, min_cena, max_cena, jedinica, kategorija = usluga

    cena_po_jedinici = round(random.uniform(min_cena, max_cena), 2)

    if kolicina_override is not None:
        kolicina = kolicina_override
    elif jedinica in ("sat", "strana", "dan"):
        kolicina = round(random.uniform(1, 40), 1)
    elif jedinica == "mesec":
        kolicina = random.choice([1, 2, 3, 6, 12])
    elif jedinica == "komad":
        kolicina = random.choice([1, 2, 3, 5])
    else:
        kolicina = 1.0

    stopa_pdv = STOPE_PDV["snizena"] if kategorija in ("Kancelarija",) else STOPE_PDV["opsta"]

    iznos_osnove = round(cena_po_jedinici * kolicina, 2)
    iznos_pdv    = round(iznos_osnove * stopa_pdv / 100, 2)
    ukupan_iznos = round(iznos_osnove + iznos_pdv, 2)

    return {
        "opis":           opis,
        "kategorija":     kategorija,
        "jedinicaMere":   jedinica,
        "kolicina":       kolicina,
        "cenaPoJedinici": cena_po_jedinici,
        "stopaPDV":       stopa_pdv,
        "iznosOsnove":    iznos_osnove,
        "iznosPDV":       iznos_pdv,
        "ukupanIznos":    ukupan_iznos,
    }


def generisi_fakturu(
    prodavac: Optional[dict] = None,
    kupac: Optional[dict] = None,
    broj_stavki: Optional[int] = None,
    dani_do_roka: int = 15,
    broj_fakture: Optional[str] = None,
) -> dict:
    """
    Generiše kompletnu fakturu u eFaktura JSON formatu.

    Polja (srpska finansijska terminologija):
      brojFakture       → serijski broj fakture
      datumIzdavanja    → datum izdavanja
      rokPlacanja       → datum dospeća
      prodavac          → podaci o prodavcu (naziv, PIB, MB)
      kupac             → podaci o kupcu (naziv, PIB, MB)
      stavkeFakture     → lista stavki
      rekapitulacija    → zbir osnove, PDV-a i ukupnog iznosa
      podaciOPlacanju   → IBAN, model i poziv na broj
    """
    prodavac = prodavac or random.choice(PRODAVCI)
    kupac    = kupac    or random.choice(KUPCI)

    # Prodavac i kupac ne smeju biti isti
    while kupac["pib"] == prodavac.get("pib"):
        kupac = random.choice(KUPCI)

    broj_stavki = broj_stavki or random.randint(1, 4)
    stavke = [generisi_stavku_fakture() for _ in range(broj_stavki)]

    # Ukupni iznosi
    ukupno_osnova = round(sum(s["iznosOsnove"] for s in stavke), 2)
    ukupno_pdv    = round(sum(s["iznosPDV"]    for s in stavke), 2)
    ukupno_iznos  = round(ukupno_osnova + ukupno_pdv, 2)

    ts             = _sada_utc()
    datum_izdavanja = ts.date().isoformat()
    rok_placanja    = (ts.date() + timedelta(days=dani_do_roka)).isoformat()
    ts_str          = ts.strftime("%Y-%m-%dT%H:%M:%SZ")

    br_fakture = broj_fakture or _sledeci_broj_fakture()

    return {
        "podaci": {
            "faktura": {
                "identifikatorFakture": str(uuid.uuid4()),
                "brojFakture":          br_fakture,
                "datumIzdavanja":       datum_izdavanja,
                "rokPlacanja":          rok_placanja,
                "valuta":               "RSD",
                "status":               "izdata",
                "prodavac": {
                    "naziv": prodavac["naziv"],
                    "pib":   prodavac["pib"],
                    "mb":    prodavac.get("mb", ""),
                },
                "kupac": {
                    "naziv": kupac["naziv"],
                    "pib":   kupac["pib"],
                    "mb":    kupac.get("mb", ""),
                },
                "stavkeFakture": stavke,
                "rekapitulacija": {
                    "iznosOsnove":  ukupno_osnova,
                    "iznosPDV":     ukupno_pdv,
                    "ukupanIznos":  ukupno_iznos,
                },
                "podaciOPlacanju": {
                    "iban":         f"RS35{random.randint(100,999):03d}{''.join([str(random.randint(0,9)) for _ in range(16)])}",
                    "model":        "97",
                    "pozivNaBroj":  f"{random.randint(10,99)}-{random.randint(1000,9999)}-{random.randint(10,99)}",
                },
            }
        },
        "meta": {
            "identifikatorFakture": str(uuid.uuid4()),
            "format":               "UBL-2.1-Simplified",
            "vremenskaOznaka":      ts_str,
            "izvor":                "mock_generator_v1",
        },
    }


def generisi_batch_faktura(
    broj: int = 3,
    prodavac: Optional[dict] = None,
) -> list[dict]:
    """Generiše batch faktura."""
    return [
        generisi_fakturu(prodavac=prodavac, dani_do_roka=random.choice([7, 15, 30, 45]))
        for _ in range(broj)
    ]


def generate_full_invoice_payload(
    count: int = 2,
    seller_index: Optional[int] = None,
) -> dict:
    """
    Glavni entry point — generiše batch faktura spreman za bazu.

    Poziva se iz ingestion servisa svakih N minuta.

    Vraća:
        {
            "fakture":       [<lista faktura>],
            "ukupnoFaktura": float,
            "broj":          int,
        }
    """
    prodavac = PRODAVCI[seller_index] if seller_index is not None else None
    fakture  = generisi_batch_faktura(broj=count, prodavac=prodavac)
    ukupno   = sum(
        f["podaci"]["faktura"]["rekapitulacija"]["ukupanIznos"] for f in fakture
    )

    return {
        "fakture":       fakture,
        "ukupnoFaktura": round(ukupno, 2),
        "broj":          len(fakture),
    }


# ─── Quick test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("=== Batch Faktura ===")
    payload = generate_full_invoice_payload(count=2)
    print(json.dumps(payload, indent=2, ensure_ascii=False))