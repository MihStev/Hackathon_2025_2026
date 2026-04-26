import sqlite3
from database import get_db_connection
from datetime import datetime

def citaj_bazu_sql(sql_upit: str) -> str:
    """
    Izvršava SELECT SQL upite nad bazom.
    Struktura tabela: 
    1. zaposleni (id, ime_prezime, osnovna_neto_plata)
    2. troskovi (id, naziv_troska, kategorija, tip_troska, iznos_rsd, datum_nastanka)
    3. fakture (broj_fakture, datum_izdavanja, rok_placanja, pib_kupca, naziv_kupca, pib_prodavca, valuta, ukupan_iznos)
    4. stavke_fakture (id, broj_fakture, opis, kolicina, cena_po_jedinici, procenat_poreza, ukupno)
    5. snimci_racuna (id, identifikator, iban, stanje_ocekivano, stanje_raspolozivo, valuta, vremenska_oznaka)
    6. transakcije (id, identifikator_transakcije, identifikator_racuna, datum_knjizenja, iznos, valuta, vrsta_transakcije, naziv_poverioca, naziv_duznika)
    """
    if not sql_upit.strip().upper().startswith("SELECT"):
        return "Greska: Samo SELECT upiti su dozvoljeni!"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_upit)
        rezultat = cursor.fetchall()
        conn.close()
        
        # MAGIČNI TRIK ZA HAKATON: Cistimo sirovi_json iz rezultata
        prociscen_rezultat =[]
        for row in rezultat:
            row_dict = dict(row)
            if 'sirovi_json' in row_dict:
                del row_dict['sirovi_json'] # Brisanje teškog polja
            prociscen_rezultat.append(row_dict)
            
        # Vraćamo AI-u čiste podatke
        return str(prociscen_rezultat)
    except Exception as e:
        return f"SQL Greska: {str(e)}"

def dodaj_trosak(naziv_troska: str, kategorija: str, tip_troska: str, iznos_rsd: float) -> str:
    """
    Dodaje novi trošak u bazu. 
    Kategorije: 'kancelarija', 'oprema', 'softver', 'ostalo'. 
    Tipovi: 'fiksni', 'jednokratni'.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        datum = datetime.now().strftime("%Y-%m-%d") # Stavljamo danasnji datum
        cursor.execute(
            "INSERT INTO troskovi (naziv_troska, kategorija, tip_troska, iznos_rsd, datum_nastanka) VALUES (?, ?, ?, ?, ?)",
            (naziv_troska, kategorija, tip_troska, iznos_rsd, datum)
        )
        conn.commit()
        conn.close()
        return f"Uspesno dodato! Trosak {naziv_troska} u iznosu od {iznos_rsd} RSD je sacuvan."
    except Exception as e:
        return f"Greska pri upisu: {str(e)}"

def azuriraj_platu(ime_zaposlenog: str, nova_plata: float) -> str:
    """Menja (ažurira) neto platu za određenog zaposlenog."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Pretpostavka za hakaton: trazimo po imenu koristeci LIKE
        cursor.execute("UPDATE zaposleni SET osnovna_neto_plata = ? WHERE ime_prezime LIKE ?", (nova_plata, f"%{ime_zaposlenog}%"))
        
        if cursor.rowcount == 0:
            return f"Nisam pronašao zaposlenog sa imenom {ime_zaposlenog}."
            
        conn.commit()
        conn.close()
        return f"Uspesno! Plata za {ime_zaposlenog} je sada {nova_plata} RSD."
    except Exception as e:
        return f"Greska: {str(e)}"

# NOVE FUNKCIJE ZA DASHBOARD

def get_current_balance():
    """Vrati trenutno stanje na računu iz poslednjeg snimka."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stanje_raspolozivo FROM snimci_racuna ORDER BY vremenska_oznaka DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    except Exception as e:
        return f"Greska: {str(e)}"

def get_expenses_last_30_days():
    """Ukupni troškovi za poslednjih 30 dana."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(iznos_rsd) FROM troskovi WHERE datum_nastanka >= date('now', '-30 days')")
        result = cursor.fetchone()
        conn.close()
        return result[0] or 0
    except Exception as e:
        return f"Greska: {str(e)}"

def get_revenue_last_30_days():
    """Ukupni prihodi za poslednjih 30 dana (izlazne fakture)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        nas_pib = "101234567"  # Hardkodirano iz prompata
        cursor.execute("SELECT SUM(ukupan_iznos) FROM fakture WHERE datum_izdavanja >= date('now', '-30 days') AND pib_prodavca = ?", (nas_pib,))
        result = cursor.fetchone()
        conn.close()
        return result[0] or 0
    except Exception as e:
        return f"Greska: {str(e)}"

def get_expenses_by_category():
    """Rashodi grupisani po kategorijama za pie chart."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT kategorija, SUM(iznos_rsd) as total FROM troskovi GROUP BY kategorija")
        results = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in results}
    except Exception as e:
        return {}

def get_monthly_revenue_expenses():
    """Prihodi i rashodi po mesecima za poslednjih 6 meseci."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        nas_pib = "101234567"
        # Prihodi po mesecima
        cursor.execute("""
            SELECT strftime('%Y-%m', datum_izdavanja) as month, SUM(ukupan_iznos) as revenue
            FROM fakture
            WHERE datum_izdavanja >= date('now', '-6 months') AND pib_prodavca = ?
            GROUP BY month
            ORDER BY month
        """, (nas_pib,))
        revenues = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Rashodi po mesecima (troškovi + plate)
        cursor.execute("""
            SELECT strftime('%Y-%m', datum_nastanka) as month, SUM(iznos_rsd) as expenses
            FROM troskovi
            WHERE datum_nastanka >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month
        """)
        expenses = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Plate po mesecima (pretpostavimo da su mesečne, koristimo trenutne plate)
        cursor.execute("SELECT SUM(osnovna_neto_plata) FROM zaposleni")
        total_salaries = cursor.fetchone()[0] or 0
        # Za svaki mesec dodaj plate (jednostavna pretpostavka)
        months = [f"{2026 - (i//12):04d}-{(i%12)+1:02d}" for i in range(6)]  # Poslednjih 6 meseci
        for month in months:
            expenses[month] = expenses.get(month, 0) + total_salaries
        
        conn.close()
        return revenues, expenses
    except Exception as e:
        return {}, {}

def get_recent_activities():
    """Nedavne aktivnosti: poslednjih 10 troškova i faktura."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 'trošak' as tip, naziv_troska as opis, iznos_rsd as iznos, datum_nastanka as datum
            FROM troskovi
            ORDER BY datum_nastanka DESC LIMIT 10
        """)
        troskovi = cursor.fetchall()
        cursor.execute("""
            SELECT 'faktura' as tip, broj_fakture as opis, ukupan_iznos as iznos, datum_izdavanja as datum
            FROM fakture
            ORDER BY datum_izdavanja DESC LIMIT 10
        """)
        fakture = cursor.fetchall()
        conn.close()
        activities = troskovi + fakture
        activities.sort(key=lambda x: x[3], reverse=True)  # Sortiraj po datumu
        return activities[:10]
    except Exception as e:
        return []

def get_upcoming_obligations():
    """Predstojeće obaveze: sledeći datumi plata, neplaćene fakture."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Plate: Pretpostavimo sledeći mesec
        cursor.execute("SELECT ime_prezime, osnovna_neto_plata FROM zaposleni")
        zaposleni = cursor.fetchall()
        obligations = []
        for z in zaposleni:
            obligations.append(('plata', f"Plata za {z[0]}", z[1], '2026-05-01'))  # Sledeći mesec
        
        # Neplaćene fakture (pretpostavimo da su neplaćene ako nema statusa)
        cursor.execute("SELECT broj_fakture, ukupan_iznos, rok_placanja FROM fakture WHERE rok_placanja >= date('now')")
        fakture = cursor.fetchall()
        for f in fakture:
            obligations.append(('faktura', f"Plati fakturu {f[0]}", f[1], f[2]))
        
        conn.close()
        obligations.sort(key=lambda x: x[3])  # Sortiraj po datumu
        return obligations[:10]
    except Exception as e:
        return []

# POREZI
def calculate_pdv(faktura_iznos):
    """PDV 20% na fakturu."""
    return faktura_iznos * 0.20

def calculate_corporate_tax(profit):
    """Porez na dobit 15%."""
    return profit * 0.15

def calculate_salary_tax(neto_plata):
    """Porez na platu 60% - izračunaj brutto."""
    return neto_plata / (1 - 0.60)

# ANALITIČKE FUNKCIJE ZA DASHBOARD

def get_yoy_comparison():
    """Poređenje tekućeg kvartala sa istim kvartalom prethodne godine."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        nas_pib = "101234567"
        
        # Trenutni kvartal
        current_quarter = (datetime.now().month - 1) // 3 + 1
        current_year = datetime.now().year
        
        # Prethodni kvartal iste godine
        prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
        prev_year = current_year if current_quarter > 1 else current_year - 1
        
        # Prihodi za trenutni kvartal
        cursor.execute("""
            SELECT SUM(ukupan_iznos) as revenue
            FROM fakture
            WHERE strftime('%Y', datum_izdavanja) = ? 
            AND ((strftime('%m', datum_izdavanja) - 1) / 3 + 1) = ?
            AND pib_prodavca = ?
        """, (str(current_year), current_quarter, nas_pib))
        current_revenue = cursor.fetchone()[0] or 0
        
        # Prihodi za prethodni kvartal
        cursor.execute("""
            SELECT SUM(ukupan_iznos) as revenue
            FROM fakture
            WHERE strftime('%Y', datum_izdavanja) = ? 
            AND ((strftime('%m', datum_izdavanja) - 1) / 3 + 1) = ?
            AND pib_prodavca = ?
        """, (str(prev_year), prev_quarter, nas_pib))
        prev_revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        return {
            'current_quarter': current_revenue,
            'previous_quarter': prev_revenue,
            'growth': ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        }
    except Exception as e:
        return {'error': str(e)}

def get_golden_month():
    """Najuspešniji mesec po profitu/prihodu."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        nas_pib = "101234567"
        
        # Prihodi po mesecima
        cursor.execute("""
            SELECT strftime('%Y-%m', datum_izdavanja) as month, SUM(ukupan_iznos) as revenue
            FROM fakture
            WHERE pib_prodavca = ?
            GROUP BY month
            ORDER BY revenue DESC
            LIMIT 1
        """, (nas_pib,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'month': result[0], 'revenue': result[1]}
        return {'month': 'N/A', 'revenue': 0}
    except Exception as e:
        return {'error': str(e)}

def calculate_health_score():
    """Izračunava ponderisanu vrednost health score (0-100)."""
    try:
        # Likvidnost (30%): Odnos trenutnog keša i dospelih obaveza
        current_balance = get_current_balance()
        upcoming_obligations = get_upcoming_obligations()
        total_obligations = sum([obl[2] for obl in upcoming_obligations if obl[0] == 'faktura'])  # Samo fakture
        liquidity_ratio = current_balance / total_obligations if total_obligations > 0 else 1
        liquidity_score = min(liquidity_ratio * 50, 50)  # Max 50 points
        
        # Profitna marža (30%): Odnos iz izdatih faktura naspram operativnih troškova
        revenue_30 = get_revenue_last_30_days()
        expenses_30 = get_expenses_last_30_days()
        profit_margin = (revenue_30 - expenses_30) / revenue_30 if revenue_30 > 0 else 0
        margin_score = max(min(profit_margin * 100, 30), 0)  # Max 30 points
        
        # Progres ka ciljevima (40%): Procenat ispunjenosti OKR-ova
        okr_progress = get_goal_progress()
        avg_progress = sum([okr['progress'] for okr in okr_progress]) / len(okr_progress) if okr_progress else 0
        goal_score = avg_progress * 0.4  # Max 40 points
        
        total_score = liquidity_score + margin_score + goal_score
        
        return {
            'score': round(total_score, 1),
            'liquidity': round(liquidity_score, 1),
            'margin': round(margin_score, 1),
            'goals': round(goal_score, 1),
            'diagnostics': f"Likvidnost: {liquidity_ratio:.2f}, Marža: {profit_margin:.2%}, OKR progres: {avg_progress:.1%}"
        }
    except Exception as e:
        return {'error': str(e)}

def get_goal_progress():
    """Progres ka OKR ciljevima."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT naziv, cilj_vrednost, trenutna_vrednost FROM okr_goals")
        results = cursor.fetchall()
        conn.close()
        progress = []
        for row in results:
            progress_pct = (row[2] / row[1]) * 100 if row[1] > 0 else 0
            progress.append({
                'goal': row[0],
                'current': row[2],
                'target': row[1],
                'progress': min(progress_pct, 100)
            })
        return progress
    except Exception as e:
        return []

def forecast_cash_flow(days=90):
    """Projekcija cash flow-a za narednih 30/60/90 dana."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        nas_pib = "101234567"
        
        # Trenutni saldo
        current_balance = get_current_balance()
        
        # Očekivani prilivi: Otvorene fakture (pretpostavimo da će biti plaćene u proseku za 30 dana)
        cursor.execute("""
            SELECT SUM(ukupan_iznos) as pending_revenue
            FROM fakture
            WHERE pib_prodavca = ? AND rok_placanja >= date('now')
        """, (nas_pib,))
        pending_revenue = cursor.fetchone()[0] or 0
        
        # Poznati odlivi: Plate, fiksni troškovi
        cursor.execute("SELECT SUM(osnovna_neto_plata) FROM zaposleni")
        monthly_salaries = cursor.fetchone()[0] or 0
        
        # Fiksni troškovi mesečno
        cursor.execute("SELECT SUM(iznos_rsd) FROM troskovi WHERE tip_troska = 'fiksni'")
        monthly_fixed = cursor.fetchone()[0] or 0
        
        # Prosečni neto cash-flow iz prošlih meseci
        cursor.execute("""
            SELECT AVG(net_flow) FROM (
                SELECT strftime('%Y-%m', t.datum_knjizenja) as month, SUM(t.iznos) as net_flow
                FROM transakcije t
                GROUP BY month
                ORDER BY month DESC LIMIT 3
            )
        """)
        avg_net_flow = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Projekcija
        forecast = []
        balance = current_balance
        for day in range(0, days + 1, 30):
            # Dodaj prilive (distribuirano)
            inflows = pending_revenue * (30 / days) if day > 0 else 0
            # Oduzmi odlive
            outflows = (monthly_salaries + monthly_fixed) * (day / 30) if day > 0 else 0
            # Proxy trend
            trend = avg_net_flow * (day / 30) if day > 0 else 0
            
            balance += inflows - outflows + trend
            forecast.append({
                'day': day,
                'balance': max(balance, 0),  # Ne može biti negativno za forecast
                'inflows': inflows,
                'outflows': outflows,
                'trend': trend
            })
        
        # Smart alerts
        alerts = []
        if balance < 0:
            alerts.append("Kritičan manjak likvidnosti u narednih 90 dana!")
        if avg_net_flow < 0:
            alerts.append("Trend troškova brže raste od priliva.")
        
        return {
            'forecast': forecast,
            'alerts': alerts,
            'confidence': 0.7  # Placeholder
        }
    except Exception as e:
        return {'error': str(e)}

def get_ai_insights():
    """Generiše AI uvide na osnovu trenutnih podataka."""
    try:
        from ai_agent import generate_ai_insights
        
        # Prikupljanje podataka za summary
        yoy = get_yoy_comparison()
        golden = get_golden_month()
        health = calculate_health_score()
        
        data_summary = f"""
        YoY poređenje: Trenutni kvartal {yoy.get('current_quarter', 0):.0f} RSD, prethodni {yoy.get('previous_quarter', 0):.0f} RSD, rast {yoy.get('growth', 0):.1f}%.
        Zlatni mesec: {golden.get('month', 'N/A')} sa prihodom {golden.get('revenue', 0):.0f} RSD.
        Health score: {health.get('score', 0)} sa dijagnostikom: {health.get('diagnostics', '')}.
        """
        
        return generate_ai_insights(data_summary)
    except Exception as e:
        return f"Greška: {str(e)}"