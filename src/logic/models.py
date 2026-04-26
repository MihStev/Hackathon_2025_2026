"""
src/logic/models.py — Pydantic modeli za validaciju podataka

Koristi se za:
  1. Validaciju bank/invoice JSON-a pre upisa u bazu
  2. Serializaciju odgovora API-ja
  3. Type hints u celom projektu

Nazivi polja prate srpsku finansijsku terminologiju.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ─── Enumi ────────────────────────────────────────────────────────────────────

class VrstaTransakcije(str, Enum):
    ODOBRENJE = "ODO"   # Odobrenje — priliv na račun
    ZADUZENJE = "ZAD"   # Zaduženje — odliv sa računa

class StatusFakture(str, Enum):
    IZDATA    = "izdata"
    PLACENA   = "placena"
    DOSPELA   = "dospela"
    STORNIRANA = "stornirana"

class VrstaStanja(str, Enum):
    OCEKIVANO   = "ocekivano"
    RASPOLOZIVO = "raspolozivo"


# ─── Bank modeli ──────────────────────────────────────────────────────────────

class NovcaniIznos(BaseModel):
    """Iznos u određenoj valuti."""
    valuta:   str   = "RSD"
    vrednost: float

class StanjeRacuna(BaseModel):
    """Jedan red u listi stanja (ocekivano / raspolozivo)."""
    vrstaStanja:     VrstaStanja
    iznos:           NovcaniIznos
    datumPromene:    str
    referentniDatum: Optional[str] = None

class PodaciRacuna(BaseModel):
    """Matični podaci o računu."""
    identifikator: str
    valuta:        str = "RSD"
    vrstaRacuna:   str
    status:        str
    bic:           Optional[str] = None
    iban:          Optional[str] = None
    imeTitulara:   Optional[str] = None
    proizvod:      Optional[str] = None

class BankovnaTransakcija(BaseModel):
    """Jedna bankovna transakcija."""
    identifikatorTransakcije: str
    datumKnjizenja:           str
    datumValute:              Optional[str] = None
    iznos:                    NovcaniIznos
    nazivPoverioca:           Optional[str] = None
    nazivDuznika:             Optional[str] = None
    svrhaPlacanja:            Optional[str] = None
    kodTransakcije:           Optional[str] = None
    kategorija:               Optional[str] = None

class SnimakRacuna(BaseModel):
    """Snimak stanja računa (balances endpoint)."""
    racun:  PodaciRacuna
    stanja: List[StanjeRacuna]


# ─── Invoice modeli ───────────────────────────────────────────────────────────

class UcesnikFakture(BaseModel):
    """Prodavac ili kupac na fakturi."""
    naziv: str
    pib:   str
    mb:    Optional[str] = None

class StavkaFakture(BaseModel):
    """Jedna stavka na fakturi."""
    opis:           str
    kategorija:     Optional[str] = None
    jedinicaMere:   Optional[str] = None
    kolicina:       float
    cenaPoJedinici: float
    stopaPDV:       float = 20.0
    iznosOsnove:    float
    iznosPDV:       float
    ukupanIznos:    float

class Rekapitulacija(BaseModel):
    """Zbir osnove, PDV-a i ukupnog iznosa fakture."""
    iznosOsnove: float
    iznosPDV:    float
    ukupanIznos: float

class PodaciOPlacanju(BaseModel):
    """IBAN, model i poziv na broj za plaćanje."""
    iban:        Optional[str] = None
    model:       Optional[str] = None
    pozivNaBroj: Optional[str] = None

class Faktura(BaseModel):
    """Kompletna faktura u eFaktura JSON formatu."""
    identifikatorFakture: str
    brojFakture:          str
    datumIzdavanja:       str
    rokPlacanja:          str
    valuta:               str = "RSD"
    status:               StatusFakture = StatusFakture.IZDATA
    prodavac:             UcesnikFakture
    kupac:                UcesnikFakture
    stavkeFakture:        List[StavkaFakture]
    rekapitulacija:       Rekapitulacija
    podaciOPlacanju:      Optional[PodaciOPlacanju] = None


# ─── API Response modeli ──────────────────────────────────────────────────────

class RezimeTransakcija(BaseModel):
    """Za dashboard endpoint — pregled transakcija."""
    ukupno_odobrenja:   float
    ukupno_zaduzenja:   float
    neto_promena:       float
    broj_transakcija:   int
    top_kategorije:     dict

class RezimeFaktura(BaseModel):
    """Za dashboard endpoint — pregled faktura."""
    ukupno_fakturisano: float
    broj_faktura:       int
    broj_dospelih:      int
    broj_placenih:      int

class PodaciDashboard(BaseModel):
    """Kompletan odgovor za dashboard."""
    tekuce_stanje:      float
    raspolozivo_stanje: float
    transakcije:        RezimeTransakcija
    fakture:            RezimeFaktura
    poslednje_azuriranje: str