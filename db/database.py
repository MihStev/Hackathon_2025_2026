"""
db/database.py — SQLite baza podataka za Google Nexus

Čuva:
  - snimci_racuna     → stanje računa po vremenskoj oznaci
  - transakcije       → svaka bankovna transakcija
  - fakture           → svaka faktura (sa stavkama kao JSON)
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "nexus.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Kreira tabele ako ne postoje."""
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS snimci_racuna (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            identifikator       TEXT    NOT NULL,
            iban                TEXT,
            stanje_ocekivano    REAL,
            stanje_raspolozivo  REAL,
            valuta              TEXT    DEFAULT 'RSD',
            vremenska_oznaka    TEXT    NOT NULL,
            sirovi_json         TEXT    NOT NULL,
            kreirano            TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS transakcije (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            identifikator_transakcije   TEXT    UNIQUE NOT NULL,
            identifikator_racuna        TEXT    NOT NULL,
            datum_knjizenja             TEXT,
            datum_valute                TEXT,
            iznos                       REAL    NOT NULL,
            valuta                      TEXT    DEFAULT 'RSD',
            vrsta_transakcije           TEXT,
            kategorija                  TEXT,
            svrha_placanja              TEXT,
            naziv_poverioca             TEXT,
            naziv_duznika               TEXT,
            sirovi_json                 TEXT    NOT NULL,
            kreirano                    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS fakture (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            identifikator_fakture   TEXT    UNIQUE NOT NULL,
            broj_fakture            TEXT,
            datum_izdavanja         TEXT,
            rok_placanja            TEXT,
            status                  TEXT    DEFAULT 'izdata',
            naziv_prodavca          TEXT,
            pib_prodavca            TEXT,
            naziv_kupca             TEXT,
            pib_kupca               TEXT,
            iznos_osnove            REAL,
            iznos_pdv               REAL,
            ukupan_iznos            REAL,
            valuta                  TEXT    DEFAULT 'RSD',
            stavke_json             TEXT,
            sirovi_json             TEXT    NOT NULL,
            kreirano                TEXT    DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_tx_racun      ON transakcije(identifikator_racuna);
        CREATE INDEX IF NOT EXISTS idx_tx_datum      ON transakcije(datum_knjizenja);
        CREATE INDEX IF NOT EXISTS idx_tx_kategorija ON transakcije(kategorija);
        CREATE INDEX IF NOT EXISTS idx_fak_prodavac  ON fakture(pib_prodavca);
        CREATE INDEX IF NOT EXISTS idx_fak_kupac     ON fakture(pib_kupca);
        CREATE INDEX IF NOT EXISTS idx_fak_rok       ON fakture(rok_placanja);
        """)
    print(f"[DB] Baza inicijalizovana: {DB_PATH}")


def insert_bank_payload(payload: dict) -> dict:
    """
    Upisuje bank payload u bazu.

    Očekuje strukturu iz generate_full_bank_payload():
        {
            "snimak":      {...},   ← stanje računa
            "transakcije": [...],   ← lista transakcija
            "novo_stanje": float,
        }

    Vraća:
        {"snimci_upisani": int, "transakcije_upisane": int}
    """
    snimak      = payload.get("snimak", {})
    transakcije = payload.get("transakcije", [])

    br_snimaka = 0
    br_tx      = 0

    with get_connection() as conn:
        # ── Snimak stanja računa ──────────────────────────────────────────────
        racun  = snimak.get("podaci", {}).get("racun", {})
        stanja = snimak.get("podaci", {}).get("stanja", [])
        meta   = snimak.get("meta", {})

        stanje_ocek  = next(
            (s["iznos"]["vrednost"] for s in stanja if s.get("vrstaStanja") == "ocekivano"), None
        )
        stanje_raspo = next(
            (s["iznos"]["vrednost"] for s in stanja if s.get("vrstaStanja") == "raspolozivo"), None
        )

        conn.execute("""
            INSERT INTO snimci_racuna
                (identifikator, iban, stanje_ocekivano, stanje_raspolozivo,
                 valuta, vremenska_oznaka, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            racun.get("identifikator", "nepoznato"),
            racun.get("iban"),
            stanje_ocek,
            stanje_raspo,
            racun.get("valuta", "RSD"),
            meta.get("vremenskaOznaka", datetime.now(timezone.utc).isoformat()),
            json.dumps(snimak, ensure_ascii=False),
        ))
        br_snimaka += 1

        # ── Transakcije ───────────────────────────────────────────────────────
        id_racuna = racun.get("identifikator", "nepoznato")
        for tx in transakcije:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO transakcije
                        (identifikator_transakcije, identifikator_racuna,
                         datum_knjizenja, datum_valute,
                         iznos, valuta, vrsta_transakcije, kategorija,
                         svrha_placanja, naziv_poverioca, naziv_duznika, sirovi_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx.get("identifikatorTransakcije"),
                    id_racuna,
                    tx.get("datumKnjizenja"),
                    tx.get("datumValute"),
                    tx.get("iznos", {}).get("vrednost", 0),
                    tx.get("iznos", {}).get("valuta", "RSD"),
                    tx.get("kodTransakcije"),
                    tx.get("kategorija"),
                    tx.get("svrhaPlacanja"),
                    tx.get("nazivPoverioca"),
                    tx.get("nazivDuznika"),
                    json.dumps(tx, ensure_ascii=False),
                ))
                br_tx += 1
            except sqlite3.IntegrityError:
                pass  # Duplikat, preskačemo

    return {"snimci_upisani": br_snimaka, "transakcije_upisane": br_tx}


def insert_invoice_payload(payload: dict) -> dict:
    """
    Upisuje invoice payload u bazu.

    Očekuje strukturu iz generate_full_invoice_payload():
        {
            "fakture":       [...],
            "ukupnoFaktura": float,
            "broj":          int,
        }

    Vraća:
        {"fakture_upisane": int}
    """
    fakture   = payload.get("fakture", [])
    br_faktura = 0

    with get_connection() as conn:
        for omotac in fakture:
            fak  = omotac.get("podaci", {}).get("faktura", {})
            meta = omotac.get("meta", {})

            try:
                conn.execute("""
                    INSERT OR IGNORE INTO fakture
                        (identifikator_fakture, broj_fakture, datum_izdavanja, rok_placanja, status,
                         naziv_prodavca, pib_prodavca, naziv_kupca, pib_kupca,
                         iznos_osnove, iznos_pdv, ukupan_iznos, valuta,
                         stavke_json, sirovi_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fak.get("identifikatorFakture") or meta.get("identifikatorFakture"),
                    fak.get("brojFakture"),
                    fak.get("datumIzdavanja"),
                    fak.get("rokPlacanja"),
                    fak.get("status", "izdata"),
                    fak.get("prodavac", {}).get("naziv"),
                    fak.get("prodavac", {}).get("pib"),
                    fak.get("kupac", {}).get("naziv"),
                    fak.get("kupac", {}).get("pib"),
                    fak.get("rekapitulacija", {}).get("iznosOsnove"),
                    fak.get("rekapitulacija", {}).get("iznosPDV"),
                    fak.get("rekapitulacija", {}).get("ukupanIznos"),
                    fak.get("valuta", "RSD"),
                    json.dumps(fak.get("stavkeFakture", []), ensure_ascii=False),
                    json.dumps(omotac, ensure_ascii=False),
                ))
                br_faktura += 1
            except sqlite3.IntegrityError:
                pass

    return {"fakture_upisane": br_faktura}


def get_recent_balance(identifikator: str = None) -> dict | None:
    """Vraća poslednji snimak stanja računa."""
    with get_connection() as conn:
        if identifikator:
            red = conn.execute(
                "SELECT * FROM snimci_racuna WHERE identifikator=? ORDER BY id DESC LIMIT 1",
                (identifikator,)
            ).fetchone()
        else:
            red = conn.execute(
                "SELECT * FROM snimci_racuna ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(red) if red else None


if __name__ == "__main__":
    init_db()
    print("[DB] OK — sve tabele postoje.")