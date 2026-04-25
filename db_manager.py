"""
db_manager.py — SQLite baza: Zaposleni i Fiksni_Troskovi
Hakaton MVP | FinAssist AI
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


# ── Konekcija ────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Rezultati kao dict-like objekti
    return conn


# ── Kreiranje tabela ─────────────────────────────────────────────────────────

def init_db():
    """Kreira tabele ako ne postoje i puni ih seed podacima."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Zaposleni (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ime         TEXT    NOT NULL,
            prezime     TEXT    NOT NULL,
            pozicija    TEXT    NOT NULL,
            sektor      TEXT    NOT NULL,
            neto_plata  REAL    NOT NULL,
            datum_od    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Fiksni_Troskovi (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv       TEXT    NOT NULL,
            kategorija  TEXT    NOT NULL,
            iznos       REAL    NOT NULL,
            period      TEXT    NOT NULL CHECK(period IN ('mesecno', 'godisnje')),
            dobavljac   TEXT    NOT NULL,
            aktivan     INTEGER NOT NULL DEFAULT 1
        );
    """)

    conn.commit()

    # Seed samo ako su tabele prazne
    if cur.execute("SELECT COUNT(*) FROM Zaposleni").fetchone()[0] == 0:
        _seed_zaposleni(cur)

    if cur.execute("SELECT COUNT(*) FROM Fiksni_Troskovi").fetchone()[0] == 0:
        _seed_fiksni_troskovi(cur)

    conn.commit()
    conn.close()
    print(f"[db] Baza inicijalizovana: {DB_PATH}")


# ── Seed podaci ──────────────────────────────────────────────────────────────

def _seed_zaposleni(cur):
    zaposleni = [
        ("Marko",     "Jovanović",  "Senior Developer",       "IT",          145000, "2021-03-01"),
        ("Jovana",    "Petrović",   "Product Manager",        "Produkt",     155000, "2020-06-15"),
        ("Nikola",    "Đorđević",   "Backend Developer",      "IT",          130000, "2022-01-10"),
        ("Milica",    "Stojanović", "UX/UI Designer",         "Dizajn",      115000, "2022-04-01"),
        ("Stefan",    "Nikolić",    "DevOps Engineer",        "IT",          140000, "2021-09-01"),
        ("Ana",       "Marković",   "Financial Analyst",      "Finansije",   125000, "2020-11-01"),
        ("Vladimir",  "Popović",    "Sales Manager",          "Prodaja",     135000, "2019-07-01"),
        ("Jelena",    "Lazović",    "HR Specialist",          "HR",          105000, "2023-02-01"),
        ("Aleksandar","Vasić",      "Junior Developer",       "IT",           90000, "2023-06-01"),
        ("Maja",      "Đukić",      "Marketing Specialist",   "Marketing",   100000, "2022-10-01"),
    ]
    cur.executemany(
        "INSERT INTO Zaposleni (ime, prezime, pozicija, sektor, neto_plata, datum_od) VALUES (?,?,?,?,?,?)",
        zaposleni
    )
    print(f"[db] Seed: {len(zaposleni)} zaposlenih upisano.")


def _seed_fiksni_troskovi(cur):
    troskovi = [
        # naziv,                         kategorija,    iznos,    period,     dobavljac
        ("Zakup kancelarije",            "Zakup",       120000,   "mesecno",  "Poslovni Centar Beograd d.o.o."),
        ("Microsoft 365 Business",       "Softver",      24000,   "mesecno",  "Microsoft Ireland Operations Ltd."),
        ("Adobe Creative Cloud",         "Softver",      18600,   "mesecno",  "Adobe Systems EMEA Ltd."),
        ("Internet - SBB",               "Komunalije",    6800,   "mesecno",  "SBB d.o.o."),
        ("Struja - EPS",                 "Komunalije",   19850,   "mesecno",  "EPS Distribucija d.o.o."),
        ("Gorivo za vozni park",         "Transport",    15200,   "mesecno",  "OMV Srbija d.o.o."),
        ("Marketing - digitalne kampanje","Marketing",   45000,   "mesecno",  "Digital Media Group d.o.o."),
        ("Pravne usluge - retainer",     "Usluge",       55000,   "mesecno",  "Advokatska kancelarija Petrovic i Jankovic"),
        ("Kancelarijski materijal",      "Kancelarija",   8500,   "mesecno",  "Papir Servis d.o.o."),
        ("Godisnja revizija",            "Usluge",      180000,   "godisnje", "BDO Srbija d.o.o."),
        ("Osiguranje opreme",            "Osiguranje",   36000,   "godisnje", "Generali Osiguranje Srbija"),
        ("Servis vozila",                "Transport",    65000,   "godisnje", "Auto centar Milosevic d.o.o."),
    ]
    cur.executemany(
        "INSERT INTO Fiksni_Troskovi (naziv, kategorija, iznos, period, dobavljac) VALUES (?,?,?,?,?)",
        troskovi
    )
    print(f"[db] Seed: {len(troskovi)} fiksnih troškova upisano.")


# ── Čitanje: Zaposleni ───────────────────────────────────────────────────────

def get_all_zaposleni() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Zaposleni ORDER BY sektor, prezime").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ukupna_masa_plata() -> float:
    conn = get_connection()
    result = conn.execute("SELECT SUM(neto_plata) FROM Zaposleni").fetchone()[0]
    conn.close()
    return result or 0.0

def get_zaposleni_po_sektoru() -> dict:
    conn = get_connection()
    rows = conn.execute(
        "SELECT sektor, COUNT(*) as broj, SUM(neto_plata) as ukupno FROM Zaposleni GROUP BY sektor ORDER BY ukupno DESC"
    ).fetchall()
    conn.close()
    return {r["sektor"]: {"broj": r["broj"], "ukupno_plata": r["ukupno"]} for r in rows}


# ── Čitanje: Fiksni Troškovi ─────────────────────────────────────────────────

def get_all_fiksni_troskovi() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM Fiksni_Troskovi WHERE aktivan=1 ORDER BY kategorija, iznos DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_mesecni_fiksni_troskovi() -> float:
    """Vraća ukupne mesečne fiksne troškove (godišnje deli na 12)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT iznos, period FROM Fiksni_Troskovi WHERE aktivan=1"
    ).fetchall()
    conn.close()
    ukupno = 0.0
    for r in rows:
        ukupno += r["iznos"] if r["period"] == "mesecno" else r["iznos"] / 12
    return ukupno

def get_fiksni_troskovi_po_kategoriji() -> dict:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT kategorija,
               SUM(CASE WHEN period='mesecno' THEN iznos ELSE iznos/12 END) as mesecno
        FROM Fiksni_Troskovi
        WHERE aktivan=1
        GROUP BY kategorija
        ORDER BY mesecno DESC
        """
    ).fetchall()
    conn.close()
    return {r["kategorija"]: round(r["mesecno"], 2) for r in rows}


# ── Pisanje ──────────────────────────────────────────────────────────────────

def add_zaposleni(ime: str, prezime: str, pozicija: str, sektor: str,
                  neto_plata: float, datum_od: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO Zaposleni (ime, prezime, pozicija, sektor, neto_plata, datum_od) VALUES (?,?,?,?,?,?)",
        (ime, prezime, pozicija, sektor, neto_plata, datum_od)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def add_fiksni_trosak(naziv: str, kategorija: str, iznos: float,
                      period: str, dobavljac: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO Fiksni_Troskovi (naziv, kategorija, iznos, period, dobavljac) VALUES (?,?,?,?,?)",
        (naziv, kategorija, iznos, period, dobavljac)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


# ── Reset (korisno za hakaton demo) ─────────────────────────────────────────

def reset_db():
    """Briše i ponovo kreira bazu — korisno tokom razvoja."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[db] Stara baza obrisana.")
    init_db()


# ── Test ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reset_db()
    print()

    zaposleni = get_all_zaposleni()
    print(f"Zaposlenih ukupno : {len(zaposleni)}")
    print(f"Masa plata        : {get_ukupna_masa_plata():,.2f} RSD / mesec")

    print("\nZaposleni po sektoru:")
    for sektor, info in get_zaposleni_po_sektoru().items():
        print(f"  {sektor:<12} | {info['broj']} zaposlena/ih | {info['ukupno_plata']:>10,.2f} RSD")

    print(f"\nMesecni fiksni troskovi: {get_mesecni_fiksni_troskovi():,.2f} RSD")

    print("\nFiksni troskovi po kategoriji (mesecno):")
    for kat, iznos in get_fiksni_troskovi_po_kategoriji().items():
        print(f"  {kat:<15}: {iznos:>10,.2f} RSD")