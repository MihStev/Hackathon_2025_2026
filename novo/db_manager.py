import json
import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── SQLite lokalna baza ──
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

Base = declarative_base()


# ════════════════════════════════════════════════════════════
# TABELE — FAKTURE
# ════════════════════════════════════════════════════════════

class Faktura(Base):
    __tablename__ = 'fakture'

    broj_fakture    = Column(String, primary_key=True)
    datum_izdavanja = Column(Date, nullable=False)
    rok_placanja    = Column(Date)
    pib_kupca       = Column(String, nullable=False)
    naziv_kupca     = Column(String)
    pib_prodavca    = Column(String, nullable=False)
    valuta          = Column(String(3))
    ukupan_iznos    = Column(Numeric(15, 2))
    sirovi_json     = Column(Text)
    azurirano       = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class StavkaFakture(Base):
    __tablename__ = 'stavke_fakture'

    id               = Column(Integer, primary_key=True, autoincrement=True)
    broj_fakture     = Column(String, ForeignKey('fakture.broj_fakture', ondelete='CASCADE'))
    opis             = Column(Text, nullable=False)
    kolicina         = Column(Numeric(15, 4))
    cena_po_jedinici = Column(Numeric(15, 2))
    procenat_poreza  = Column(Numeric(5, 2))
    ukupno           = Column(Numeric(15, 2))


# ════════════════════════════════════════════════════════════
# TABELE — BANKARSKI RAČUNI
# ════════════════════════════════════════════════════════════

class BankovniRacun(Base):
    __tablename__ = 'bankovni_racuni'

    iban          = Column(String, primary_key=True)          # RS35160000000012345678
    identifikator = Column(String, unique=True)               # UUID iz banke
    valuta        = Column(String(3))                         # RSD
    vrsta_racuna  = Column(String)                            # Tekući račun
    status        = Column(String)                            # aktivan / blokiran
    bic           = Column(String(11))                        # DBSSDEFF
    ime_titulara  = Column(String)                            # Stefan Branković
    proizvod      = Column(String)                            # Tekući račun - Standard
    azurirano     = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class StanjeRacuna(Base):
    __tablename__ = 'stanja_racuna'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    iban            = Column(String, ForeignKey('bankovni_racuni.iban', ondelete='CASCADE'))
    vrsta_stanja    = Column(String)                          # ocekivano / raspolozivo
    vrednost        = Column(Numeric(15, 2))
    valuta          = Column(String(3))
    datum_promene   = Column(DateTime)
    referentni_datum = Column(Date)
    azurirano       = Column(DateTime, default=datetime.now)


# ════════════════════════════════════════════════════════════
# INIT
# ════════════════════════════════════════════════════════════

def init_db():
    """Kreira sve tabele ako ne postoje. Bezbedno za višestruko pozivanje."""
    Base.metadata.create_all(engine)
    logger.info("Baza inicijalizovana: database.db (fakture + bankovni računi)")


# ════════════════════════════════════════════════════════════
# PROCESS — FAKTURE
# ════════════════════════════════════════════════════════════

def process_efaktura(json_data: Dict[str, Any], session):
    """Upsert fakture i njenih stavki u bazu."""
    invoice_data = json_data.get("podaci", {}).get("faktura", {}) or json_data.get("data", {}).get("invoice", {})
    if not invoice_data:
        logger.error("Nema podataka o fakturi u JSON-u.")
        return

    broj_fakture = invoice_data.get("brojFakture") or invoice_data.get("invoiceNumber")
    datum_str    = invoice_data.get("datumIzdavanja") or invoice_data.get("issueDate")
    rok_str      = invoice_data.get("rokPlacanja") or invoice_data.get("dueDate")
    kupac        = invoice_data.get("kupac", {}) or invoice_data.get("buyerParty", {})
    prodavac     = invoice_data.get("prodavac", {}) or invoice_data.get("sellerParty", {})
    uslovi       = invoice_data.get("uslovi", {}) or invoice_data.get("totals", {})

    header_info = {
        "broj_fakture":    broj_fakture,
        "datum_izdavanja": datetime.strptime(datum_str, "%Y-%m-%d").date(),
        "rok_placanja":    datetime.strptime(rok_str, "%Y-%m-%d").date() if rok_str else None,
        "pib_kupca":       kupac.get("pib"),
        "naziv_kupca":     kupac.get("naziv") or kupac.get("name"),
        "pib_prodavca":    prodavac.get("pib"),
        "valuta":          invoice_data.get("valuta") or invoice_data.get("currency"),
        "ukupan_iznos":    uslovi.get("ukupno") or uslovi.get("totalAmount"),
        "sirovi_json":     json.dumps(json_data, ensure_ascii=False),
    }

    existing = session.query(Faktura).filter(Faktura.broj_fakture == broj_fakture).first()
    if existing:
        for key, value in header_info.items():
            setattr(existing, key, value)
        session.query(StavkaFakture).filter(StavkaFakture.broj_fakture == broj_fakture).delete()
    else:
        session.add(Faktura(**header_info))

    stavke = invoice_data.get("stavke", []) or invoice_data.get("invoiceItem", [])
    for item in stavke:
        session.add(StavkaFakture(
            broj_fakture     = broj_fakture,
            opis             = item.get("opis") or item.get("description"),
            kolicina         = item.get("kolicina") or item.get("quantity"),
            cena_po_jedinici = item.get("cenaPoDingli") or item.get("unitPrice"),
            procenat_poreza  = item.get("procenatPoreza") or item.get("taxPercentage"),
            ukupno           = item.get("ukupno") or item.get("total"),
        ))

    try:
        session.commit()
        logger.info(f"Faktura {broj_fakture} upisana sa {len(stavke)} stavki.")
    except Exception as e:
        session.rollback()
        logger.error(f"Greška pri upisu fakture: {e}")


# ════════════════════════════════════════════════════════════
# PROCESS — BANKARSKI RAČUN
# ════════════════════════════════════════════════════════════

def process_racun(json_data: Dict[str, Any], session):
    """Upsert bankovnog računa i njegovih stanja u bazu."""
    podaci = json_data.get("podaci", {})
    racun  = podaci.get("racun", {})

    if not racun:
        logger.error("Nema podataka o računu u JSON-u.")
        return

    iban = racun.get("iban")
    if not iban:
        logger.error("IBAN nije pronađen u JSON-u.")
        return

    racun_info = {
        "iban":          iban,
        "identifikator": racun.get("identifikator"),
        "valuta":        racun.get("valuta"),
        "vrsta_racuna":  racun.get("vrstaRacuna"),
        "status":        racun.get("status"),
        "bic":           racun.get("bic"),
        "ime_titulara":  racun.get("imeTitulara"),
        "proizvod":      racun.get("proizvod"),
    }

    existing = session.query(BankovniRacun).filter(BankovniRacun.iban == iban).first()
    if existing:
        for key, value in racun_info.items():
            setattr(existing, key, value)
        # Brišemo stara stanja — upisujemo sveža
        session.query(StanjeRacuna).filter(StanjeRacuna.iban == iban).delete()
        logger.info(f"Račun {iban} ažuriran.")
    else:
        session.add(BankovniRacun(**racun_info))
        logger.info(f"Račun {iban} dodat.")

    stanja = podaci.get("stanja", [])
    for s in stanja:
        iznos = s.get("iznos", {})
        datum_promene_str   = s.get("datumPromene")
        referentni_datum_str = s.get("referentniDatum")

        session.add(StanjeRacuna(
            iban             = iban,
            vrsta_stanja     = s.get("vrstaStanja"),
            vrednost         = iznos.get("vrednost"),
            valuta           = iznos.get("valuta"),
            datum_promene    = datetime.fromisoformat(datum_promene_str.replace("Z", "+00:00")) if datum_promene_str else None,
            referentni_datum = datetime.strptime(referentni_datum_str, "%Y-%m-%d").date() if referentni_datum_str else None,
        ))

    try:
        session.commit()
        logger.info(f"Stanja za račun {iban} upisana ({len(stanja)} stavki).")
    except Exception as e:
        session.rollback()
        logger.error(f"Greška pri upisu računa: {e}")


# ════════════════════════════════════════════════════════════
# DISPEČER
# ════════════════════════════════════════════════════════════

def process_data(json_data: Dict[str, Any], session):
    """Automatski detektuje tip JSON-a i prosleđuje odgovarajućoj funkciji."""
    podaci = json_data.get("podaci", {})

    if podaci.get("racun"):
        process_racun(json_data, session)
    elif podaci.get("faktura") or json_data.get("data", {}).get("invoice"):
        process_efaktura(json_data, session)
    else:
        fmt = json_data.get("meta", {}).get("format", "")
        if "UBL" in fmt:
            process_efaktura(json_data, session)
        else:
            logger.warning(f"Nepoznat format ulaznog JSON-a. (format: '{fmt}')")


# ════════════════════════════════════════════════════════════
# HELPER FUNKCIJE za ai_agent.py
# ════════════════════════════════════════════════════════════

def get_ukupna_masa_plata() -> float:
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT SUM(neto_plata) FROM Zaposleni")
            val = result.scalar()
            return float(val) if val else 0.0
    except Exception:
        return 0.0


def get_mesecni_fiksni_troskovi() -> float:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                "SELECT SUM(CASE WHEN ucestalost='mesecno' THEN iznos ELSE iznos/12.0 END) FROM Fiksni_Troskovi"
            )
            val = result.scalar()
            return float(val) if val else 0.0
    except Exception:
        return 0.0


def get_fiksni_troskovi_po_kategoriji() -> list:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                "SELECT kategorija, SUM(iznos) FROM Fiksni_Troskovi GROUP BY kategorija ORDER BY SUM(iznos) DESC"
            )
            return [(row[0], float(row[1])) for row in result]
    except Exception:
        return []


def get_zaposleni_po_sektoru() -> list:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                "SELECT sektor, COUNT(*), SUM(neto_plata) FROM Zaposleni GROUP BY sektor ORDER BY SUM(neto_plata) DESC"
            )
            return [(row[0], row[1], float(row[2])) for row in result]
    except Exception:
        return []


# ════════════════════════════════════════════════════════════
# TEST
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()

    # Test: faktura
    sample_faktura = {
        "data": {
            "invoice": {
                "invoiceNumber": "F-2026-0001",
                "issueDate": "2026-04-25",
                "dueDate": "2026-05-10",
                "currency": "RSD",
                "sellerParty": {"name": "Moja Firma DOO", "pib": "101234567"},
                "buyerParty":  {"name": "Kupac Partner",  "pib": "107654321"},
                "invoiceItem": [
                    {"description": "Razvoj AI Modela", "quantity": 1.0,
                     "unitPrice": 50000.0, "taxPercentage": 20.0, "total": 60000.0}
                ],
                "totals": {"netAmount": 50000.0, "taxAmount": 10000.0, "totalAmount": 60000.0},
            }
        },
        "meta": {"format": "UBL-2.1-Simplified", "timestamp": "2026-04-25T16:09:00Z"},
    }

    # Test: bankarski račun
    sample_racun = {
        "podaci": {
            "racun": {
                "identifikator": "c9c223a0-1234-5678-90ab-cdef12345678",
                "valuta": "RSD",
                "vrstaRacuna": "Tekući račun",
                "status": "aktivan",
                "bic": "DBSSDEFF",
                "iban": "RS35160000000012345678",
                "imeTitulara": "Stefan Branković",
                "proizvod": "Tekući račun - Standard"
            },
            "stanja": [
                {
                    "vrstaStanja": "ocekivano",
                    "iznos": {"valuta": "RSD", "vrednost": 144505.88},
                    "datumPromene": "2026-04-26T00:51:36Z",
                    "referentniDatum": "2026-04-26"
                },
                {
                    "vrstaStanja": "raspolozivo",
                    "iznos": {"valuta": "RSD", "vrednost": 143189.59},
                    "datumPromene": "2026-04-26T00:51:36Z",
                    "referentniDatum": None
                }
            ]
        },
        "meta": {"ukupnoRezultata": 2, "vremenskaOznaka": "2026-04-26T00:51:36Z"}
    }

    session = Session()
    process_data(sample_faktura, session)
    process_data(sample_racun, session)
    session.close()

    # Provera
    session = Session()
    f = session.query(Faktura).first()
    r = session.query(BankovniRacun).first()
    s = session.query(StanjeRacuna).all()
    print(f"\n✅ Faktura:  {f.broj_fakture} | {f.naziv_kupca} | {f.ukupan_iznos} RSD")
    print(f"✅ Račun:    {r.iban} | {r.ime_titulara} | {r.vrsta_racuna}")
    for stanje in s:
        print(f"   Stanje [{stanje.vrsta_stanja}]: {stanje.vrednost} RSD")
    session.close()