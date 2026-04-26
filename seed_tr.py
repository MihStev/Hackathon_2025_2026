import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "finassist.db")

# PIB naše firme
NAS_PIB = "101234567"

def seed_database():
    if not os.path.exists(DB_PATH):
        print(f"Baza ne postoji na putanji: {DB_PATH}. Prvo pokreni aplikaciju da se kreira struktura.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Počinjem punjenje baze podacima...")

        # ==========================================
        # 1. ZAPOSLENI (15 zaposlenih – različite plate, odeljenja i senioriteti)
        # ==========================================
        zaposleni_data = [
            # (ime_prezime, osnovna_neto_plata)
            ('Ana Anić',            145000),   # Senior Developer
            ('Marko Marković',      115000),   # Mid Developer
            ('Jelena Jovanović',    130000),   # Product Manager
            ('Nikola Nikolić',       95000),   # Junior Developer
            ('Marija Marić',        125000),   # QA Lead
            ('Petar Petrović',      110000),   # DevOps Engineer
            ('Svetlana Svetić',     138000),   # UX/UI Designer
            ('Dragan Dragić',        98000),   # Junior Designer
            ('Milica Milićević',    155000),   # CTO
            ('Stefan Stefanović',   120000),   # Backend Developer
            ('Ivana Ivanović',      105000),   # Marketing Specialist
            ('Aleksandar Aleksić',  142000),   # Data Scientist
            ('Tijana Tijić',         92000),   # Support Specialist
            ('Vladimir Vladić',     118000),   # Frontend Developer
            ('Katarina Katić',      165000),   # CEO / Direktor
        ]
        cursor.executemany(
            "INSERT INTO zaposleni (ime_prezime, osnovna_neto_plata) VALUES (?, ?)",
            zaposleni_data
        )

        # ==========================================
        # 2. TROŠKOVI (30 stavki – fiksni + jednokratni, razni meseci)
        # ==========================================
        troskovi_data = [
            # naziv_troska | kategorija | tip_troska | iznos_rsd | datum_nastanka

            # --- Februar 2026 ---
            ('Zakup kancelarije – feb',          'kancelarija',    'fiksni',      100000, '2026-02-01'),
            ('Internet i telefonija – feb',       'komunikacije',   'fiksni',       28000, '2026-02-05'),
            ('Kafa, voda i osveženje – feb',      'kancelarija',    'fiksni',       12000, '2026-02-01'),
            ('Računovodstvene usluge – feb',      'računovodstvo',  'fiksni',       45000, '2026-02-03'),
            ('Adobe Creative Cloud – feb',        'softver',        'fiksni',       22000, '2026-02-01'),
            ('GitHub Teams licenca',              'softver',        'jednokratni',  18000, '2026-02-10'),
            ('Kancelarijski materijal',           'kancelarija',    'jednokratni',  19500, '2026-02-14'),
            ('Tim building radionica',            'obuka',          'jednokratni',  55000, '2026-02-20'),
            ('Popravka klima uređaja',            'održavanje',     'jednokratni',  32000, '2026-02-22'),

            # --- Mart 2026 ---
            ('Zakup kancelarije – mar',           'kancelarija',    'fiksni',      100000, '2026-03-01'),
            ('Internet i telefonija – mar',        'komunikacije',   'fiksni',       28000, '2026-03-05'),
            ('Kafa, voda i osveženje – mar',       'kancelarija',    'fiksni',       12000, '2026-03-01'),
            ('Računovodstvene usluge – mar',       'računovodstvo',  'fiksni',       45000, '2026-03-03'),
            ('Adobe Creative Cloud – mar',         'softver',        'fiksni',       22000, '2026-03-01'),
            ('Godišnja licenca Jira/Confluence',   'softver',        'jednokratni',  95000, '2026-03-08'),
            ('Oprema za video konferencije',       'IT oprema',      'jednokratni',  78000, '2026-03-12'),
            ('Dizajn brošura i štampanje',         'marketing',      'jednokratni',  38000, '2026-03-15'),
            ('Kurs – React Advanced',              'obuka',          'jednokratni',  42000, '2026-03-18'),
            ('Prekovremeni prevod dokumentacije',  'ostalo',         'jednokratni',  15000, '2026-03-25'),
            ('Servis štampača i toneri',           'IT oprema',      'jednokratni',  21000, '2026-03-28'),

            # --- April 2026 ---
            ('Zakup kancelarije – apr',           'kancelarija',    'fiksni',      135000, '2026-04-01'),
            ('Internet i telefonija – apr',        'komunikacije',   'fiksni',       28000, '2026-04-01'),
            ('Kafa, voda i osveženje – apr',       'kancelarija',    'fiksni',       12000, '2026-04-01'),
            ('Računovodstvene usluge – apr',       'računovodstvo',  'fiksni',       45000, '2026-04-03'),
            ('Adobe Creative Cloud – apr',         'softver',        'fiksni',       22000, '2026-04-01'),
            ('Google Workspace licenca',           'softver',        'fiksni',       31000, '2026-04-01'),
            ('Marketing kampanja – Google Ads',    'marketing',      'jednokratni',  20000, '2026-04-05'),
            ('Nabavka laptopova (3 kom.)',          'IT oprema',      'jednokratni',  35000, '2026-04-10'),
            ('Poslovna putovanja – Beograd/Zagreb','putni troškovi', 'jednokratni',  67000, '2026-04-16'),
            ('Pravne usluge – ugovor sa klijentom','pravne usluge',  'jednokratni',  55000, '2026-04-21'),
        ]
        cursor.executemany(
            "INSERT INTO troskovi (naziv_troska, kategorija, tip_troska, iznos_rsd, datum_nastanka) VALUES (?, ?, ?, ?, ?)",
            troskovi_data
        )

        # ==========================================
        # 3. FAKTURE IZLAZNE (Mi smo prodavac – pib_prodavca = NAS_PIB)
        #    8 faktura u periodu feb–apr 2026
        # ==========================================
        fakture_izlazne = [
            # broj_fakture | datum_izdavanja | rok_placanja | pib_kupca | naziv_kupca | pib_prodavca | valuta | ukupan_iznos | sirovi_json
            ('F-2026-001', '2026-02-03', '2026-02-18', '107654321', 'Klijent DOO',        NAS_PIB, 'RSD',  180000.00,
             json.dumps({"detalji": "Razvoj AI Asistenta – faza 1", "napomena": "Avansno plaćanje 30%"})),

            ('F-2026-002', '2026-02-20', '2026-03-07', '112233445', 'TechCorp AD',        NAS_PIB, 'RSD',  240000.00,
             json.dumps({"detalji": "Konsultantske usluge – feb 2026", "napomena": ""})),

            ('F-2026-003', '2026-03-01', '2026-03-16', '223344556', 'StartUp IO',         NAS_PIB, 'RSD',   96000.00,
             json.dumps({"detalji": "UX Dizajn – sprint 1 i 2", "napomena": "Popust 5% za rani partner"})),

            ('F-2026-004', '2026-03-10', '2026-03-25', '334455667', 'Digitale Serbia doo',NAS_PIB, 'RSD',  312000.00,
             json.dumps({"detalji": "Backend razvoj – Q1 2026", "napomena": ""})),

            ('F-2026-005', '2026-03-22', '2026-04-06', '445566778', 'Nexum Systems AD',   NAS_PIB, 'RSD',  156000.00,
             json.dumps({"detalji": "Data Engineering usluge", "napomena": "Mesečni retejner"})),

            ('F-2026-006', '2026-04-01', '2026-04-16', '107654321', 'Klijent DOO',        NAS_PIB, 'RSD',  210000.00,
             json.dumps({"detalji": "Razvoj AI Asistenta – faza 2", "napomena": ""})),

            ('F-2026-007', '2026-04-12', '2026-04-27', '556677889', 'Nova Era doo',       NAS_PIB, 'RSD',  144000.00,
             json.dumps({"detalji": "DevOps konzultacije i CI/CD setup", "napomena": ""})),

            ('F-2026-008', '2026-04-22', '2026-05-07', '667788990', 'Balkan Tech Group',  NAS_PIB, 'RSD',  1032000.00,
             json.dumps({"detalji": "Razvoj mobilne aplikacije – faza 1", "napomena": "Milestoni: 50% po isporuci"})),

            ('F-2026-009', '2026-02-10', '2026-02-25', '112233445', 'TechCorp AD',        NAS_PIB, 'RSD',  350000.00,
             json.dumps({"detalji": "Razvoj modula za predikciju", "napomena": ""})),

            ('F-2026-010', '2026-02-28', '2026-03-15', '223344556', 'StartUp IO',         NAS_PIB, 'RSD',  280000.00,
             json.dumps({"detalji": "Održavanje sistema – Q1", "napomena": ""})),

            ('F-2026-011', '2026-03-15', '2026-03-30', '334455667', 'Digitale Serbia doo',NAS_PIB, 'RSD',  460000.00,
             json.dumps({"detalji": "Cloud migracija – faza 1", "napomena": ""})),

            ('F-2026-012', '2026-03-28', '2026-04-12', '445566778', 'Nexum Systems AD',   NAS_PIB, 'RSD',  216000.00,
             json.dumps({"detalji": "Security audit", "napomena": ""})),

            ('F-2026-013', '2026-04-05', '2026-04-20', '107654321', 'Klijent DOO',        NAS_PIB, 'RSD',  130000.00,
             json.dumps({"detalji": "Dodatne konsultacije", "napomena": ""})),

            ('F-2026-014', '2026-04-28', '2026-05-13', '556677889', 'Nova Era doo',       NAS_PIB, 'RSD',  126000.00,
             json.dumps({"detalji": "API Integracija", "napomena": ""})),
        ]
        cursor.executemany("""
            INSERT INTO fakture (broj_fakture, datum_izdavanja, rok_placanja, pib_kupca, naziv_kupca,
                                 pib_prodavca, valuta, ukupan_iznos, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fakture_izlazne)

        stavke_izlazne = [
            # broj_fakture | opis | kolicina | cena_po_jedinici | procenat_poreza | ukupno
            ('F-2026-001', 'Razvoj AI Asistenta – faza 1',           1,  150000.00, 20.0,  180000.00),
            ('F-2026-002', 'Konsultacije – februar 2026',             1,  200000.00, 20.0,  240000.00),
            ('F-2026-003', 'UX Dizajn – sprint 1',                   1,   48000.00, 20.0,   57600.00),
            ('F-2026-003', 'UX Dizajn – sprint 2',                   1,   32000.00, 20.0,   38400.00),
            ('F-2026-004', 'Backend razvoj – jan-mar 2026',           3,   86666.67, 20.0,  312000.00),
            ('F-2026-005', 'Data Engineering – mesečni retejner',     1,  130000.00, 20.0,  156000.00),
            ('F-2026-006', 'Razvoj AI Asistenta – faza 2',            1,  175000.00, 20.0,  210000.00),
            ('F-2026-007', 'DevOps konzultacije',                     4,   26666.67, 20.0,  128000.10),
            ('F-2026-007', 'CI/CD setup i dokumentacija',             1,   13333.33, 20.0,   16000.00),
            ('F-2026-008', 'Mobilna aplikacija – iOS i Android',      1,  860000.00, 20.0, 1032000.00),
            ('F-2026-009', 'Razvoj modula za predikciju',           1,  291666.67, 20.0,  350000.00),
            ('F-2026-010', 'Održavanje sistema – Q1',               1,  233333.33, 20.0,  280000.00),
            ('F-2026-011', 'Cloud migracija – faza 1',              1,  383333.33, 20.0,  460000.00),
            ('F-2026-012', 'Security audit i izveštaj',             1,  180000.00, 20.0,  216000.00),
            ('F-2026-013', 'Konsultacije – april',                  1,  108333.33, 20.0,  130000.00),
            ('F-2026-014', 'API Integracija sa ERP-om',             1,  105000.00, 20.0,  126000.00),
        ]
        cursor.executemany("""
            INSERT INTO stavke_fakture (broj_fakture, opis, kolicina, cena_po_jedinici, procenat_poreza, ukupno)
            VALUES (?, ?, ?, ?, ?, ?)
        """, stavke_izlazne)

        # ==========================================
        # 4. FAKTURE ULAZNE (Mi smo kupac – pib_kupca = NAS_PIB)
        #    6 faktura od dobavljača
        # ==========================================
        fakture_ulazne = [
            # broj_fakture | datum_izdavanja | rok_placanja | pib_kupca | naziv_kupca | pib_prodavca | valuta | ukupan_iznos | sirovi_json
            ('U-2026-041', '2026-02-10', '2026-02-25', NAS_PIB, 'Moja Firma DOO', '111222333', 'RSD',  54000.00,
             json.dumps({"detalji": "Kancelarijski nameštaj", "napomena": "3 radna stola + stolice"})),

            ('U-2026-042', '2026-02-20', '2026-03-07', NAS_PIB, 'Moja Firma DOO', '222333444', 'RSD',  95000.00,
             json.dumps({"detalji": "Godišnja MS Office licenca (5 korisnika)", "napomena": "Obnova"})),

            ('U-2026-043', '2026-03-05', '2026-03-20', NAS_PIB, 'Moja Firma DOO', '334455667', 'RSD',  78000.00,
             json.dumps({"detalji": "Jira + Confluence godišnji plan", "napomena": "10 korisnika"})),

            ('U-2026-044', '2026-03-18', '2026-04-02', NAS_PIB, 'Moja Firma DOO', '445566778', 'RSD',  38000.00,
             json.dumps({"detalji": "Dizajn logotipa i brend identiteta", "napomena": "Agencija DesignPro"})),

            ('U-2026-045', '2026-04-08', '2026-04-23', NAS_PIB, 'Moja Firma DOO', '556677889', 'RSD', 285000.00,
             json.dumps({"detalji": "Nabavka laptopova – 3 kom. (MacBook Pro)", "napomena": "Serijski brojevi priloženi"})),

            ('U-2026-046', '2026-04-20', '2026-05-05', NAS_PIB, 'Moja Firma DOO', '667788990', 'RSD',  55000.00,
             json.dumps({"detalji": "Pravne usluge – izrada ugovora i NDA", "napomena": "Advokatska kancelarija Pravović"})),
        ]
        cursor.executemany("""
            INSERT INTO fakture (broj_fakture, datum_izdavanja, rok_placanja, pib_kupca, naziv_kupca,
                                 pib_prodavca, valuta, ukupan_iznos, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fakture_ulazne)

        stavke_ulazne = [
            ('U-2026-041', 'Kancelarijski stolovi (3 kom.)',          3,  13333.33, 20.0,  48000.00),
            ('U-2026-041', 'Ergonomske stolice (3 kom.)',             3,   2000.00, 20.0,   7200.00),  # pribl.
            # Prilagođeno tako da zbir odgovara ukupnom iznosu fakture
            ('U-2026-042', 'MS Office 365 Business – 5 korisnika',   5,  15833.33, 20.0,  95000.00),
            ('U-2026-043', 'Jira Software Cloud (10 users)',          1,  38333.33, 20.0,  46000.00),
            ('U-2026-043', 'Confluence Cloud (10 users)',             1,  26666.67, 20.0,  32000.00),
            ('U-2026-044', 'Dizajn logotipa',                        1,  20000.00, 20.0,  24000.00),
            ('U-2026-044', 'Brand guidelines dokument',              1,  11666.67, 20.0,  14000.00),
            ('U-2026-045', 'MacBook Pro 14" M3 (3 kom.)',            3,  79166.67, 20.0, 285000.00),
            ('U-2026-046', 'Izrada ugovora o saradnji',              2,  18333.33, 20.0,  44000.00),
            ('U-2026-046', 'NDA – Non-Disclosure Agreement',         1,   9166.67, 20.0,  11000.00),
        ]
        cursor.executemany("""
            INSERT INTO stavke_fakture (broj_fakture, opis, kolicina, cena_po_jedinici, procenat_poreza, ukupno)
            VALUES (?, ?, ?, ?, ?, ?)
        """, stavke_ulazne)

        # ==========================================
        # 5. BANKA: SNIMCI RAČUNA (2 preseka – kraj februara i danas)
        # ==========================================
        cursor.execute("""
            INSERT INTO snimci_racuna (identifikator, iban, stanje_ocekivano, stanje_raspolozivo,
                                       valuta, vremenska_oznaka, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'RACUN-1',
            'RS35160000001234567890',
            620000.00, 620000.00, 'RSD',
            '2026-02-28 23:59:00',
            json.dumps({"status": "Aktivno", "dozvoljeni_minus": 0, "napomena": "Presek krajem februara"})
        ))
        cursor.execute("""
            INSERT INTO snimci_racuna (identifikator, iban, stanje_ocekivano, stanje_raspolozivo,
                                       valuta, vremenska_oznaka, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'RACUN-2',
            'RS35160000001234567890',
            1_148_000.00, 1_148_000.00, 'RSD',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps({"status": "Aktivno", "dozvoljeni_minus": 0, "napomena": "Aktuelni presek"})
        ))

        # ==========================================
        # 6. BANKA: TRANSAKCIJE (40 transakcija – feb, mar, apr 2026)
        # ==========================================
        # Format: id | id_racuna | datum_knjizenja | datum_valute | iznos | valuta |
        #         vrsta | kategorija | svrha | naziv_poverioca | naziv_duznika | sirovi_json
        intesa = json.dumps({"banka": "Intesa", "provizija": 0})

        transakcije_data = [

            # ======= FEBRUAR: PRIHODI =======
            ('TRX-2001', 'RACUN-1', '2026-02-18', '2026-02-18',  180000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-001', 'Moja Firma DOO', 'Klijent DOO',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-001"})),

            ('TRX-2002', 'RACUN-1', '2026-02-25', '2026-02-25',  240000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-002', 'Moja Firma DOO', 'TechCorp AD',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-002"})),

            # ======= FEBRUAR: PLATE =======
            ('TRX-2003', 'RACUN-1', '2026-02-01', '2026-02-01',   -75000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Ana Anić', 'Ana Anić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 37})),

            ('TRX-2004', 'RACUN-1', '2026-02-01', '2026-02-01',   -45000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Marko Marković', 'Marko Marković', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 22})),

            ('TRX-2005', 'RACUN-1', '2026-02-01', '2026-02-01',   -60000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Jelena Jovanović', 'Jelena Jovanović', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 30})),

            ('TRX-2006', 'RACUN-1', '2026-02-01', '2026-02-01',   -25000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Nikola Nikolić', 'Nikola Nikolić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 12})),

            ('TRX-2007', 'RACUN-1', '2026-02-01', '2026-02-01',   -85000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Milica Milićević', 'Milica Milićević', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 42})),

            ('TRX-2008', 'RACUN-1', '2026-02-01', '2026-02-01',  -100000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za januar – Katarina Katić', 'Katarina Katić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 50})),

            # ======= FEBRUAR: TROŠKOVI =======
            ('TRX-2009', 'RACUN-1', '2026-02-01', '2026-02-01',  -100000.00, 'RSD', 'odliv',
             'Trošak', 'Zakup kancelarije – feb', 'Poslovni Centar doo', 'Moja Firma DOO', intesa),

            ('TRX-2010', 'RACUN-1', '2026-02-05', '2026-02-05',   -28000.00, 'RSD', 'odliv',
             'Trošak', 'Internet i telefonija – feb', 'Telekom Srbija', 'Moja Firma DOO', intesa),

            ('TRX-2011', 'RACUN-1', '2026-02-14', '2026-02-14',   -19500.00, 'RSD', 'odliv',
             'Trošak', 'Kancelarijski materijal', 'Papirus doo', 'Moja Firma DOO', intesa),

            ('TRX-2012', 'RACUN-1', '2026-02-20', '2026-02-20',   -55000.00, 'RSD', 'odliv',
             'Trošak', 'Tim building radionica', 'TeamEvent RS doo', 'Moja Firma DOO', intesa),

            # ======= MART: PRIHODI =======
            ('TRX-3001', 'RACUN-2', '2026-03-10', '2026-03-10',   96000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-003', 'Moja Firma DOO', 'StartUp IO',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-003"})),

            ('TRX-3002', 'RACUN-2', '2026-03-20', '2026-03-20',  312000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-004', 'Moja Firma DOO', 'Digitale Serbia doo',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-004"})),

            ('TRX-3003', 'RACUN-2', '2026-03-30', '2026-03-30',  156000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-005', 'Moja Firma DOO', 'Nexum Systems AD',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-005"})),

            # ======= MART: PLATE =======
            ('TRX-3004', 'RACUN-2', '2026-03-01', '2026-03-01',   -75000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Ana Anić', 'Ana Anić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 37})),

            ('TRX-3005', 'RACUN-2', '2026-03-01', '2026-03-01',   -45000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Marko Marković', 'Marko Marković', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 22})),

            ('TRX-3006', 'RACUN-2', '2026-03-01', '2026-03-01',   -60000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Jelena Jovanović', 'Jelena Jovanović', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 30})),

            ('TRX-3007', 'RACUN-2', '2026-03-01', '2026-03-01',   -25000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Nikola Nikolić', 'Nikola Nikolić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 12})),

            ('TRX-3008', 'RACUN-2', '2026-03-01', '2026-03-01',   -85000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Milica Milićević', 'Milica Milićević', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 42})),

            ('TRX-3009', 'RACUN-2', '2026-03-01', '2026-03-01',  -100000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za februar – Katarina Katić', 'Katarina Katić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 50})),

            # ======= MART: TROŠKOVI =======
            ('TRX-3010', 'RACUN-2', '2026-03-01', '2026-03-01',  -100000.00, 'RSD', 'odliv',
             'Trošak', 'Zakup kancelarije – mar', 'Poslovni Centar doo', 'Moja Firma DOO', intesa),

            ('TRX-3011', 'RACUN-2', '2026-03-08', '2026-03-08',   -95000.00, 'RSD', 'odliv',
             'Trošak', 'Jira/Confluence godišnja licenca', 'Atlassian Distributor doo', 'Moja Firma DOO', intesa),

            ('TRX-3012', 'RACUN-2', '2026-03-12', '2026-03-12',   -78000.00, 'RSD', 'odliv',
             'Trošak', 'Oprema za video konferencije', 'IT Oprema doo', 'Moja Firma DOO', intesa),

            ('TRX-3013', 'RACUN-2', '2026-03-18', '2026-03-18',   -42000.00, 'RSD', 'odliv',
             'Trošak', 'Kurs React Advanced', 'Edu Platform doo', 'Moja Firma DOO', intesa),

            # ======= APRIL: PRIHODI =======
            ('TRX-4001', 'RACUN-2', '2026-04-16', '2026-04-16',  210000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-006', 'Moja Firma DOO', 'Klijent DOO',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-006"})),

            ('TRX-4002', 'RACUN-2', '2026-04-24', '2026-04-24',  144000.00, 'RSD', 'priliv',
             'Uplata klijenta', 'Naplata F-2026-007', 'Moja Firma DOO', 'Nova Era doo',
             json.dumps({"banka": "Intesa", "provizija": 0, "faktura": "F-2026-007"})),

            # F-2026-008 još nije plaćena (rok 07.05)

            # ======= APRIL: PLATE =======
            ('TRX-4003', 'RACUN-2', '2026-04-01', '2026-04-01',  -130000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Ana Anić', 'Ana Anić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 65})),

            ('TRX-4004', 'RACUN-2', '2026-04-01', '2026-04-01',  -100000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Marko Marković', 'Marko Marković', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 50})),

            ('TRX-4005', 'RACUN-2', '2026-04-01', '2026-04-01',  -115000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Jelena Jovanović', 'Jelena Jovanović', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 57})),

            ('TRX-4006', 'RACUN-2', '2026-04-01', '2026-04-01',   -80000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Nikola Nikolić', 'Nikola Nikolić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 40})),

            ('TRX-4007', 'RACUN-2', '2026-04-01', '2026-04-01',  -140000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Milica Milićević', 'Milica Milićević', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 70})),

            ('TRX-4008', 'RACUN-2', '2026-04-01', '2026-04-01',  -150000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Katarina Katić', 'Katarina Katić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 75})),

            ('TRX-4009', 'RACUN-2', '2026-04-01', '2026-04-01',  -105000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Stefan Stefanović', 'Stefan Stefanović', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 52})),

            ('TRX-4010', 'RACUN-2', '2026-04-01', '2026-04-01',  -127000.00, 'RSD', 'odliv',
             'Plata', 'Zarada za mart – Aleksandar Aleksić', 'Aleksandar Aleksić', 'Moja Firma DOO',
             json.dumps({"banka": "Intesa", "provizija": 63})),

            # ======= APRIL: TROŠKOVI =======
            ('TRX-4011', 'RACUN-2', '2026-04-01', '2026-04-01',  -135000.00, 'RSD', 'odliv',
             'Trošak', 'Zakup kancelarije – apr', 'Poslovni Centar doo', 'Moja Firma DOO', intesa),

            ('TRX-4012', 'RACUN-2', '2026-04-05', '2026-04-05',   -20000.00, 'RSD', 'odliv',
             'Trošak', 'Google Ads kampanja – april', 'Google Ireland Ltd.', 'Moja Firma DOO', intesa),

            ('TRX-4013', 'RACUN-2', '2026-04-10', '2026-04-10',   -35000.00, 'RSD', 'odliv',
             'Trošak', 'Nabavka laptopova (3 MacBook Pro)', 'Apple Premium Reseller', 'Moja Firma DOO', intesa),

            ('TRX-4014', 'RACUN-2', '2026-04-16', '2026-04-16',   -67000.00, 'RSD', 'odliv',
             'Trošak', 'Poslovna putovanja Beograd/Zagreb', 'Aviomax Travel doo', 'Moja Firma DOO', intesa),

            ('TRX-4015', 'RACUN-2', '2026-04-21', '2026-04-21',   -55000.00, 'RSD', 'odliv',
             'Trošak', 'Pravne usluge – ugovor i NDA', 'Advokatska kancelarija Pravović', 'Moja Firma DOO', intesa),
        ]
        cursor.executemany("""
            INSERT INTO transakcije (identifikator_transakcije, identifikator_racuna, datum_knjizenja,
                                     datum_valute, iznos, valuta, vrsta_transakcije, kategorija,
                                     svrha_placanja, naziv_poverioca, naziv_duznika, sirovi_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, transakcije_data)

        # ==========================================
        # 7. OKR GOALS (6 ciljeva za Q2 2026)
        # ==========================================
        # naziv | cilj_vrednost | trenutna_vrednost | rok | kategorija
        okr_data = [
            # Prihod: cilj 500k/mes, trenutno ~354k prosek (feb+mar+apr prihodi / 3)
            ('Dostići mesečni prihod od 500.000 RSD',      500000.00,  354000.00, '2026-06-30', 'prihod'),

            # Troškovi: smanjiti fiksne mesečne troškove
            ('Smanjiti fiksne troškove ispod 300.000 RSD', 300000.00,  370000.00, '2026-06-30', 'troskovi'),

            # Klijenti: povećati broj aktivnih klijenata
            ('Povećati broj aktivnih klijenata na 8',           8,          5,    '2026-06-30', 'klijenti'),

            # Likvidnost: poboljšati DSO (Days Sales Outstanding)
            ('Smanjiti DSO ispod 25 dana',                  25.00,      38.00,    '2026-06-30', 'likvidnost'),

            # Zadovoljstvo zaposlenih: interna ocena
            ('Postići NPS zaposlenih ≥ 75',                 75.00,      62.00,    '2026-06-30', 'zadovoljstvo'),

            # Fakture: nulta neplaćenost – sve fakture naplaćene na vreme
            ('Dostiči 95% naplativost faktura na vreme',    95.00,      80.00,    '2026-06-30', 'naplativost'),
        ]
        cursor.executemany(
            "INSERT INTO okr_goals (naziv, cilj_vrednost, trenutna_vrednost, rok, kategorija) VALUES (?, ?, ?, ?, ?)",
            okr_data
        )

        conn.commit()
        print("✅ Baza je uspešno napunjena podacima!")
        print(f"   → Zaposleni:       {len(zaposleni_data)}")
        print(f"   → Troškovi:        {len(troskovi_data)}")
        print(f"   → Fakture izlazne: {len(fakture_izlazne)}")
        print(f"   → Fakture ulazne:  {len(fakture_ulazne)}")
        print(f"   → Transakcije:     {len(transakcije_data)}")
        print(f"   → OKR Goals:       {len(okr_data)}")

    except sqlite3.IntegrityError as e:
        print(f"⚠️  Podaci su verovatno već uneti. Greška: {e}")
    except Exception as e:
        print(f"❌ Došlo je do greške: {e}")
        import traceback; traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()