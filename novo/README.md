# 📋 Sistem za Upravljanje eFakturama

Sistem za čuvanje, ažuriranje i pretragu eFaktura iz JSON fajlova.

## 📁 Struktura Fajlova

```
/root/finassist-ai/novo/
├── db_manager.py          # Glavna baza i logika
├── test_azuriranje.py     # Test skripte
├── helper.py              # Helper komande
├── 1.json                 # Primer faktura #1
├── 2.json                 # Primer faktura #2
├── 3.json                 # Primer faktura #3
└── database.db            # SQLite baza (auto-kreira se)
```

## 🚀 Brz Start

### 1️⃣ Inicijalizacija baze
```bash
cd /root/finassist-ai/novo
python db_manager.py
```
Ovo će:
- Kreirati `database.db` ako ne postoji
- Učitati primer fakture F-2026-0001

### 2️⃣ Pokrenuti testove
```bash
python test_azuriranje.py
```
Testira:
- Učitavanje tri fakture iz JSON fajlova
- Ažuriranje fakture (UPSERT)
- Pretragu i analitiku

### 3️⃣ Brze operacije sa helper skriptom
```bash
# Pregled svih faktura
python helper.py sve

# Pregled konkretne fakture
python helper.py faktura F-2026-0001

# Pretraga po kupcu
python helper.py pretrazi "Kupac A"

# Statistika
python helper.py stats
```

## 📊 JSON Format eFakture

Svaki JSON fajl (1.json, 2.json, 3.json) ima ovu strukturu:

```json
{
  "data": {
    "invoice": {
      "invoiceNumber": "F-2026-0001",
      "issueDate": "2026-04-20",
      "dueDate": "2026-05-20",
      "currency": "RSD",
      "sellerParty": {
        "name": "Naziv Preduzeća",
        "pib": "101234567"
      },
      "buyerParty": {
        "name": "Kupac",
        "pib": "107654321"
      },
      "invoiceItem": [
        {
          "description": "Opis stavke",
          "quantity": 1.0,
          "unitPrice": 50000.0,
          "taxPercentage": 20.0,
          "total": 60000.0
        }
      ],
      "totals": {
        "netAmount": 50000.0,
        "taxAmount": 10000.0,
        "totalAmount": 60000.0
      }
    }
  },
  "meta": {
    "format": "UBL-2.1-Simplified",
    "timestamp": "2026-04-20T10:00:00Z"
  }
}
```

## 🔄 Ažuriranje (UPSERT)

Ako učitaš JSON sa istim `invoiceNumber`, baza će:
1. **Obrisati stare stavke** (invoice_items) za tu fakturu
2. **Ažurirati zaglavlje** (invoice header) novim podacima
3. **Dodati nove stavke** iz JSON-a

**Primer:** Ako učitaš `F-2026-0001` sa 3 stavke (umesto 2), baza će automatski ažurirati sve.

## 📊 Baza Podataka

Tabela `invoices`:
- invoice_number (Ključ)
- issue_date, due_date
- buyer_pib, buyer_name
- seller_pib
- currency
- total_amount
- raw_json (Originalni JSON)
- updated_at

Tabela `invoice_items`:
- id (Ključ)
- invoice_number (Strani ključ)
- description, quantity, unit_price
- tax_percentage, total

## 💡 Praktični Primeri

### Učitaj novu fakturu
```bash
python helper.py ucitaj 1.json
```

### Pregled svih stavki od određenog kupca
```bash
python helper.py pretrazi "Kupac A"
```

### Ukupna vrednost faktura
```bash
python helper.py stats
```

### Detaljni pregled fakture
```bash
python helper.py faktura F-2026-0001
```

## 🧪 Testovi

Test skripte verificiraju:

**Test 1 - Inicijalno učitavanje**
✅ Tri fakture učitane iz JSON fajlova
✅ Ukupno 5 stavki i 276,000 RSD

**Test 2 - UPSERT (Ažuriranje)**
✅ Faktura F-2026-0001 ažurirana
✅ Kupac promenjen, dodata stavka, vrednost povećana

**Test 3 - Pretraga i analitika**
✅ Sortiranje po vrednosti
✅ Pretraga po kupcu
✅ Izračunavanje ukupnih vrednosti

## ⚙️ Tehnički Detalji

- **Baza:** SQLite (database.db)
- **ORM:** SQLAlchemy
- **Format:** JSON (UBL-2.1-Simplified)
- **Python:** 3.12+

## 🔮 Buduće Nadogradnje

- [ ] Podrška za različite tipove dokumenata (transakcije, otpremnice, itd.)
- [ ] Vector search za semantičku pretragu opisatora stavki
- [ ] REST API za integraciju sa agentima
- [ ] Excel export izveštaja
- [ ] Migracijski script sa PostgreSQL-a

## 📝 Beleške

- JSON fajlovi moraju biti validni UBL-2.1-Simplified format
- `invoiceNumber` mora biti jedinstven (koristi se kao primarni ključ)
- Datumi moraju biti u formatu `YYYY-MM-DD`
- Sve vrednosti se čuvaju kao `Decimal` za finansijsku preciznost

---
**Verzija:** 1.0  
**Zadnja ažuriranja:** 2026-04-26
