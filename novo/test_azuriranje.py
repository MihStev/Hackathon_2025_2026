"""
Test skripte za ažuriranje baze sa tri JSON fajla.
Testira:
1. Inicijalno učitavanje tri fakture
2. Ažuriranje fakture (promenjena stavka)
3. Provera integriteta podataka
"""

import json
import os
from db_manager import init_db, Session, Faktura, StavkaFakture, process_data


def test_inicijalno_ucitavanje():
    """Test 1: Učitavanje tri fakture iz JSON fajlova"""
    print("\n" + "=" * 70)
    print("TEST 1: INICIJALNO UČITAVANJE TRI FAKTURE")
    print("=" * 70)

    init_db()
    session = Session()

    json_fajlovi = ["1.json", "2.json", "3.json"]

    for json_fajl in json_fajlovi:
        if os.path.exists(json_fajl):
            with open(json_fajl, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"\n📥 Učitavanje: {json_fajl}")
                process_data(data, session)
                broj = data.get("data", {}).get("invoice", {}).get("invoiceNumber")
                print(f"   ✅ Faktura {broj} procesirana")
        else:
            print(f"❌ Fajl {json_fajl} ne postoji!")

    session.close()

    # Provera u bazi
    session = Session()
    fakture = session.query(Faktura).all()
    print(f"\n📊 Ukupno faktura u bazi: {len(fakture)}")

    for f in fakture:
        stavke = session.query(StavkaFakture).filter(
            StavkaFakture.broj_fakture == f.broj_fakture
        ).all()
        print(f"   • {f.broj_fakture} ({f.naziv_kupca}): {len(stavke)} stavki | {f.ukupan_iznos} RSD")

    session.close()


def test_azuriranje_fakture():
    """Test 2: Ažuriranje postojeće fakture"""
    print("\n" + "=" * 70)
    print("TEST 2: AŽURIRANJE FAKTURE (UPSERT)")
    print("=" * 70)

    session = Session()

    azurirana_faktura = {
        "data": {
            "invoice": {
                "invoiceNumber": "F-2026-0001",
                "issueDate": "2026-04-20",
                "dueDate": "2026-05-20",
                "currency": "RSD",
                "sellerParty": {"name": "TechSoft DOO", "pib": "101234567"},
                "buyerParty": {"name": "Kupac A - UPDATED", "pib": "107654321"},
                "invoiceItem": [
                    {"description": "Razvoj AI Modela - VERZIJA 2", "quantity": 2.0, "unitPrice": 55000.0, "taxPercentage": 20.0, "total": 132000.0},
                    {"description": "Konzultacija - proširena",     "quantity": 10.0, "unitPrice": 12000.0, "taxPercentage": 20.0, "total": 144000.0},
                    {"description": "Support - 1 mesec",            "quantity": 1.0,  "unitPrice": 20000.0, "taxPercentage": 20.0, "total": 24000.0},
                ],
                "totals": {"netAmount": 250000.0, "taxAmount": 50000.0, "totalAmount": 300000.0}
            }
        },
        "meta": {"format": "UBL-2.1-Simplified", "timestamp": "2026-04-25T18:00:00Z"}
    }

    print("\n📝 Ažuriranje fakture F-2026-0001:")
    print("   - Promenjen kupac: 'Kupac A' → 'Kupac A - UPDATED'")
    print("   - Dodata 3. stavka (Support)")
    print("   - Nova vrednost: 300.000 RSD (umesto 120.000 RSD)")

    process_data(azurirana_faktura, session)
    session.close()

    # Provera ažuriranja
    session = Session()
    f = session.query(Faktura).filter(Faktura.broj_fakture == "F-2026-0001").first()
    stavke = session.query(StavkaFakture).filter(
        StavkaFakture.broj_fakture == "F-2026-0001"
    ).all()

    print(f"\n✅ Ažuriranje završeno:")
    print(f"   • Kupac:          {f.naziv_kupca}")
    print(f"   • Ukupna vrednost: {f.ukupan_iznos} RSD")
    print(f"   • Broj stavki:    {len(stavke)}")
    for i, s in enumerate(stavke, 1):
        print(f"     {i}. {s.opis} — {s.ukupno} RSD")

    session.close()


def test_pretraga_i_analitika():
    """Test 3: Pretraga i analitika"""
    print("\n" + "=" * 70)
    print("TEST 3: PRETRAGA I ANALITIKA")
    print("=" * 70)

    session = Session()

    fakture = session.query(Faktura).order_by(Faktura.ukupan_iznos.desc()).all()

    print(f"\n📈 Fakture sortirane po vrednosti (od većih prema manjima):")
    ukupno = 0.0
    for f in fakture:
        print(f"   {f.broj_fakture} | {f.naziv_kupca:25} | {f.ukupan_iznos:>12} RSD | {f.datum_izdavanja}")
        ukupno += float(f.ukupan_iznos)

    print(f"\n💰 Ukupna vrednost svih faktura: {ukupno:.2f} RSD")

    print(f"\n🔍 Pretraga po kupcu 'Kupac B':")
    kupac_b = session.query(Faktura).filter(Faktura.naziv_kupca.like("%Kupac B%")).all()
    if kupac_b:
        for f in kupac_b:
            stavke = session.query(StavkaFakture).filter(
                StavkaFakture.broj_fakture == f.broj_fakture
            ).all()
            print(f"   • Faktura: {f.broj_fakture}")
            for s in stavke:
                print(f"     - {s.opis}: {s.kolicina} x {s.cena_po_jedinici} = {s.ukupno}")
    else:
        print("   Nema faktura za 'Kupac B'.")

    session.close()


if __name__ == "__main__":
    import sys

    print("\n" + "🧪 POKRETANJE TESTOVA AŽURIRANJA BAZE 🧪".center(70))
    print("=" * 70)

    try:
        test_inicijalno_ucitavanje()
        test_azuriranje_fakture()
        test_pretraga_i_analitika()

        print("\n" + "=" * 70)
        print("✅ SVI TESTOVI USPEŠNO ZAVRŠENI".center(70))
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ GREŠKA TOKOM TESTOVA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)