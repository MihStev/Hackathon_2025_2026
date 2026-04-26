import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finassist.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Da vraca rezultate kao recnike (lakse za AI)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Plate: Zaposleni
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS zaposleni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime_prezime VARCHAR(100) NOT NULL,
        osnovna_neto_plata DECIMAL(10, 2) NOT NULL
    )''')

    # 2. Troskovi
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS troskovi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv_troska VARCHAR(100) NOT NULL,
        kategorija VARCHAR(50), 
        tip_troska VARCHAR(20) NOT NULL, 
        iznos_rsd DECIMAL(10, 2) NOT NULL,
        datum_nastanka DATE NOT NULL
    )''')

    # 3. Chat Istorija
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_poruke (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL DEFAULT 1,
        uloga VARCHAR(20) NOT NULL,
        sadrzaj TEXT,
        vreme DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 4. FAKTURE (Ovo je falilo!)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fakture (
        broj_fakture VARCHAR(50) PRIMARY KEY,
        datum_izdavanja DATE NOT NULL,
        rok_placanja DATE,
        pib_kupca VARCHAR(20) NOT NULL,
        naziv_kupca VARCHAR(100),
        pib_prodavca VARCHAR(20) NOT NULL,
        valuta VARCHAR(3) DEFAULT 'RSD',
        ukupan_iznos DECIMAL(15, 2),
        sirovi_json TEXT,
        azurirano DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 5. STAVKE FAKTURE (Ovo je falilo!)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stavke_fakture (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        broj_fakture VARCHAR(50) NOT NULL,
        opis TEXT NOT NULL,
        kolicina DECIMAL(15, 4),
        cena_po_jedinici DECIMAL(15, 2),
        procenat_poreza DECIMAL(5, 2),
        ukupno DECIMAL(15, 2),
        FOREIGN KEY (broj_fakture) REFERENCES fakture(broj_fakture) ON DELETE CASCADE
    )''')

    # 6. Banka - Stanje računa
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snimci_racuna (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifikator TEXT NOT NULL,
        iban TEXT,
        stanje_ocekivano REAL,
        stanje_raspolozivo REAL,
        valuta TEXT DEFAULT 'RSD',
        vremenska_oznaka TEXT NOT NULL,
        sirovi_json TEXT NOT NULL,
        kreirano TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # 7. Banka - Transakcije
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transakcije (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifikator_transakcije TEXT UNIQUE NOT NULL,
        identifikator_racuna TEXT NOT NULL,
        datum_knjizenja TEXT,
        datum_valute TEXT,
        iznos REAL NOT NULL,
        valuta TEXT DEFAULT 'RSD',
        vrsta_transakcije TEXT,
        kategorija TEXT,
        svrha_placanja TEXT,
        naziv_poverioca TEXT,
        naziv_duznika TEXT,
        sirovi_json TEXT NOT NULL,
        kreirano TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # 8. OKR Goals
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS okr_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv VARCHAR(200) NOT NULL,
        cilj_vrednost DECIMAL(15, 2) NOT NULL,
        trenutna_vrednost DECIMAL(15, 2) DEFAULT 0,
        rok DATE NOT NULL,
        kategorija VARCHAR(50) DEFAULT 'general'
    )''')
    
    conn.commit()
    conn.close()

def save_chat_message(uloga: str, sadrzaj: str, chat_id: int = 1):
    """Cuvamo samo tekstualne poruke za istoriju."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_poruke (chat_id, uloga, sadrzaj) VALUES (?, ?, ?)", (chat_id, uloga, sadrzaj))
    conn.commit()
    conn.close()

def get_chat_history(chat_id: int | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if chat_id:
        cursor.execute("SELECT uloga, sadrzaj FROM chat_poruke WHERE chat_id = ? ORDER BY vreme ASC", (chat_id,))
    else:
        cursor.execute("SELECT uloga, sadrzaj FROM chat_poruke ORDER BY vreme ASC")
    rows = cursor.fetchall()
    conn.close()
    return[{"role": row["uloga"], "content": row["sadrzaj"]} for row in rows]

def get_next_chat_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(chat_id) FROM chat_poruke")
    max_id = cursor.fetchone()[0]
    conn.close()
    return (max_id or 0) + 1

def get_chat_list():
    """Dohvata listu chatova sa naslovom (prva user poruka) i datumom."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chat_id, 
               (SELECT sadrzaj FROM chat_poruke WHERE chat_id = c.chat_id AND uloga = 'user' ORDER BY vreme ASC LIMIT 1) as naslov,
               MAX(vreme) as poslednja_poruka
        FROM chat_poruke c
        GROUP BY chat_id
        ORDER BY poslednja_poruka DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"chat_id": row["chat_id"], "naslov": row["naslov"] or "Novi Chat", "datum": row["poslednja_poruka"]} for row in rows]