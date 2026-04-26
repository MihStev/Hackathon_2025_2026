import json
import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── SQLite lokalna baza ──
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

Base = declarative_base()


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

    id              = Column(Integer, primary_key=True, autoincrement=True)
    broj_fakture    = Column(String, ForeignKey('fakture.broj_fakture', ondelete='CASCADE'))
    opis            = Column(Text, nullable=False)
    kolicina        = Column(Numeric(15, 4))
    cena_po_jedinici = Column(Numeric(15, 2))
    procenat_poreza = Column(Numeric(5, 2))
    ukupno          = Column(Numeric(15, 2))


def init_db():
    """Kreira tabele ako ne postoje. Bezbedno za višestruko pozivanje."""
    Base.metadata.create_all(engine)
    logger.info("Baza inicijalizovana: database.db")


def process_efaktura(json_data: Dict[str, Any], session):
    """Upsert fakture i njenih stavki u bazu."""
    invoice_data = json_data.get("podaci", {}).get("faktura", {}) or json_data.get("data", {}).get("invoice", {})
    if not invoice_data:
        logger.error("Nema podataka o fakturi u JSON-u.")
        return

    broj_fakture    = invoice_data.get("brojFakture") or invoice_data.get("invoiceNumber")
    datum_str       = invoice_data.get("datumIzdavanja") or invoice_data.get("issueDate")
    rok_str         = invoice_data.get("rokPlacanja") or invoice_data.get("dueDate")

    kupac           = invoice_data.get("kupac", {}) or invoice_data.get("buyerParty", {})
    prodavac        = invoice_data.get("prodavac", {}) or invoice_data.get("sellerParty", {})
    uslovi          = invoice_data.get("uslovi", {}) or invoice_data.get("totals", {})

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
        logger.error(f"Greška pri upisu: {e}")


def process_data(json_data: Dict[str, Any], session):
    """Dispečer za različite tipove ulaza."""
    fmt = json_data.get("meta", {}).get("format", "")
    if "UBL" in fmt or "eFaktura" in str(json_data):
        process_efaktura(json_data, session)
    elif "transaction" in fmt:
        logger.info("Format transakcije — još nije implementirano.")
    else:
        logger.warning(f"Nepoznat format: {fmt}")


# ── Helper funkcije za ai_agent.py ──────────────────────────────────────────

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


if __name__ == "__main__":
    init_db()

    sample_json = {
        "data": {
            "invoice": {
                "invoiceNumber": "F-2026-0001",
                "issueDate": "2026-04-25",
                "dueDate": "2026-05-10",
                "currency": "RSD",
                "sellerParty": {"name": "Moja Firma DOO", "pib": "101234567"},
                "buyerParty":  {"name": "Kupac Partner",  "pib": "107654321"},
                "invoiceItem": [
                    {
                        "description":   "Razvoj AI Modela",
                        "quantity":      1.0,
                        "unitPrice":     50000.0,
                        "taxPercentage": 20.0,
                        "total":         60000.0,
                    }
                ],
                "totals": {"netAmount": 50000.0, "taxAmount": 10000.0, "totalAmount": 60000.0},
            }
        },
        "meta": {"format": "UBL-2.1-Simplified", "timestamp": "2026-04-25T16:09:00Z"},
    }

    session = Session()
    process_data(sample_json, session)
    session.close()

    session = Session()
    f = session.query(Faktura).first()
    print(f"\n✅ Faktura u bazi: {f.broj_fakture} | {f.naziv_kupca} | {f.ukupan_iznos} RSD")
    session.close()