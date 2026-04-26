#!/usr/bin/env python3
"""
Helper skripte za brzu upotrebu baze faktura.
Omogućava:
- Učitavanje JSON fajla u bazu
- Pregled svih faktura
- Izvoz izveštaja
"""

import json
import sys
import os
from db_manager import init_db, Session, Faktura, StavkaFakture, process_data
from tabulate import tabulate


def ucitaj_json(json_file):
    """Učita JSON fajl u bazu"""
    if not os.path.exists(json_file):
        print(f"❌ Fajl '{json_file}' ne postoji!")
        return False

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        session = Session()
        process_data(data, session)
        session.close()

        inv_num = data.get("data", {}).get("invoice", {}).get("invoiceNumber")
        print(f"✅ Faktura {inv_num} uspešno učitana iz {json_file}")
        return True
    except Exception as e:
        print(f"❌ Greška pri učitavanju: {e}")
        return False


def prikazi_sve_fakture():
    """Prikazuje sve fakture u bazi"""
    session = Session()
    fakture = session.query(Faktura).order_by(Faktura.broj_fakture).all()

    if not fakture:
        print("❌ Nema faktura u bazi!")
        return

    podaci = []
    for f in fakture:
        broj_stavki = session.query(StavkaFakture).filter(
            StavkaFakture.broj_fakture == f.broj_fakture
        ).count()
        podaci.append([
            f.broj_fakture,
            f.naziv_kupca,
            f.datum_izdavanja,
            broj_stavki,
            f"{f.ukupan_iznos} RSD"
        ])

    print("\n📋 SVE FAKTURE U BAZI:")
    print(tabulate(podaci, headers=["Broj", "Kupac", "Datum", "Stavki", "Vrednost"], tablefmt="grid"))

    session.close()


def prikazi_fakturu(broj_fakture):
    """Prikazuje detalje određene fakture"""
    session = Session()
    f = session.query(Faktura).filter(Faktura.broj_fakture == broj_fakture).first()

    if not f:
        print(f"❌ Faktura {broj_fakture} ne postoji!")
        return

    print(f"\n📄 FAKTURA: {f.broj_fakture}")
    print("=" * 60)
    print(f"Kupac:       {f.naziv_kupca} (PIB: {f.pib_kupca})")
    print(f"Prodavac:    {f.pib_prodavca}")
    print(f"Datum:       {f.datum_izdavanja} | Rok: {f.rok_placanja}")
    print(f"Valuta:      {f.valuta}")
    print("=" * 60)

    stavke = session.query(StavkaFakture).filter(
        StavkaFakture.broj_fakture == broj_fakture
    ).all()

    podaci = []
    for s in stavke:
        podaci.append([
            s.opis,
            f"{s.kolicina}",
            f"{s.cena_po_jedinici} RSD",
            f"{s.procenat_poreza}%",
            f"{s.ukupno} RSD"
        ])

    print("\nSTAVKE:")
    print(tabulate(podaci, headers=["Opis", "Količina", "Cena/kom", "Porez", "Ukupno"], tablefmt="grid"))
    print(f"\nUKUPNO: {f.ukupan_iznos} RSD")

    session.close()


def pretrazi_fakture(keyword):
    """Pretraživanje faktura po kupcu ili opisu stavke"""
    session = Session()

    fakture = session.query(Faktura).filter(
        Faktura.naziv_kupca.like(f"%{keyword}%")
    ).all()

    stavke = session.query(StavkaFakture).filter(
        StavkaFakture.opis.like(f"%{keyword}%")
    ).all()

    if not fakture and not stavke:
        print(f"❌ Nema rezultata za '{keyword}'")
        return

    if fakture:
        print(f"\n🔍 REZULTATI - Kupci sa '{keyword}':")
        for f in fakture:
            print(f"  • {f.broj_fakture}: {f.naziv_kupca}")

    if stavke:
        print(f"\n🔍 REZULTATI - Stavke sa '{keyword}':")
        for s in stavke:
            print(f"  • {s.broj_fakture}: {s.opis}")

    session.close()


def statistika():
    """Prikazuje statistiku"""
    session = Session()

    fakture = session.query(Faktura).all()
    ukupno_stavki = session.query(StavkaFakture).count()

    if not fakture:
        print("❌ Nema faktura u bazi!")
        return

    ukupna_vrednost = sum(float(f.ukupan_iznos) for f in fakture)
    prosecna_vrednost = ukupna_vrednost / len(fakture)

    print("\n📊 STATISTIKA:")
    print("=" * 40)
    print(f"Ukupno faktura:      {len(fakture)}")
    print(f"Ukupno stavki:       {ukupno_stavki}")
    print(f"Ukupna vrednost:     {ukupna_vrednost:.2f} RSD")
    print(f"Prosečna vrednost:   {prosecna_vrednost:.2f} RSD")
    print("=" * 40)

    session.close()


if __name__ == "__main__":
    init_db()

    if len(sys.argv) < 2:
        print("""
🔧 HELPER - Brze operacije sa bazom faktura

UPOTREBA:
  python helper.py ucitaj <fajl>           - Učita JSON fajl
  python helper.py sve                     - Prikazuje sve fakture
  python helper.py faktura <broj>          - Prikazuje detalje
  python helper.py pretrazi <ključna reč>  - Pretraži fakture
  python helper.py stats                   - Statistika

PRIMERI:
  python helper.py ucitaj 1.json
  python helper.py sve
  python helper.py faktura F-2026-0001
  python helper.py pretrazi "Kupac A"
  python helper.py stats
""")
        sys.exit(0)

    komanda = sys.argv[1]

    if komanda == "ucitaj" and len(sys.argv) > 2:
        ucitaj_json(sys.argv[2])
    elif komanda == "sve":
        prikazi_sve_fakture()
    elif komanda == "faktura" and len(sys.argv) > 2:
        prikazi_fakturu(sys.argv[2])
    elif komanda == "pretrazi" and len(sys.argv) > 2:
        pretrazi_fakture(sys.argv[2])
    elif komanda == "stats":
        statistika()
    else:
        print(f"❌ Nepoznata komanda: {komanda}")
        sys.exit(1)