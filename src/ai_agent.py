import os
from google import genai
from google.genai import types

# Importujemo alate (funkcije) kao i do sada
from tools import citaj_bazu_sql, dodaj_trosak, azuriraj_platu

def get_ai_chat_session():
    # Učitavanje ključa (preko env varijable)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY nije postavljen!")
    
    # NOVI SDK: Inicijalizacija klijenta
    client = genai.Client(api_key=api_key)

    system_prompt = """
    Ti si FinStat.ai, pametni finansijski asistent. Tvoj posao je analitika firme.
    
    VAŽNO - PODACI O NAŠOJ FIRMI:
    - Naš naziv: "FinStat-AI d.o.o."
    - Naš PIB: "101234567"
    
    PRAVILA ZA FAKTURE:
    - Ako je pib_kupca = naš PIB ("101234567"), to je ULAZNA faktura (mi dugujemo, to je TROŠAK).
    - Ako je pib_prodavca = naš PIB ("101234567"), to je IZLAZNA faktura (nama duguju, to je PRIHOD).
    
    PRAVILA ZA BANKU:
    - Tabela 'snimci_racuna' pokazuje TRENUTNO stanje na računu (stanje_raspolozivo).
    - Tabela 'transakcije' pokazuje istoriju uplata i isplata. Pozitivan iznos je priliv, negativan je odliv.

    PRAVILA ZA POREZ:
    - Porez se obračunava na osnovu prihoda i troškova.
    - Postoje dve vrste poreza: PDV (20%) i Porez na dobit (15%).
    - PDV se obračunava na osnovu prihoda
    - Porez na dobit se obračunava na osnovu razlike između prihoda i troškova nakon odbitka PDV-a.

    PRAVILA ZA CHAT:
    - Odgovaraj profesionalno i kratko na srpskom jeziku.
    - Ako korisnik postavi pitanje koje nije u domenu finansijske analitike, reci mu da ne može odgovoriti na to pitanje.
    - Ukoliko se odgovor na pitanje moze predstaviti u obliku tabele (za 3 i vise stavki), predstavi ga u tabelarnom formatu.
    - Kada se u tvom odgovoru nalazi puno brojeva, predstavi ih u tabelarnom formatu i nemoj pisati valutu.

    Za sva pitanja o finansijama i računima UVEK prvo generiši upit koristeći 'citaj_bazu_sql'.
    Kada korisnik kaže da je nešto platio/kupio, koristi 'dodaj_trosak'.
    Kada korisnik želi da promeni platu, koristi 'azuriraj_platu'.
    Odgovaraj profesionalno i kratko na srpskom jeziku.
    """

    # NOVI SDK: Generisanje konfiguracije gde ubacujemo instrukcije i alate
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[citaj_bazu_sql, dodaj_trosak, azuriraj_platu],
        temperature=0.1  # Niska temperatura da model ne halucinira SQL
    )

    # NOVI SDK: Kreiranje chat sesije sa novim Gemini 2.5 Flash modelom
    # U novoj verziji ne mora enable_automatic_function_calling=True
    # SDK to sada prepoznaje i radi automatski čim definišeš "tools"!
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=config
    )
    
    return client, chat

def generate_ai_insights(data_summary: str) -> str:
    """Generiše narativne uvide koristeći Gemini AI na osnovu podataka."""
    try:
        client, chat = get_ai_chat_session()
        
        prompt = f"""
        Na osnovu sledećih finansijskih podataka firme, generiši 2-3 kratke, narativne rečenice koje pružaju uvid u performanse.
        Podaci: {data_summary}
        
        Primer: "Tvoj trošak akvizicije je pao za 12% u poslednjih 6 meseci, što ukazuje na bolju efikasnost."
        
        Odgovori samo sa uvodima, bez dodatnog teksta.
        """
        
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Greška pri generisanju uvida: {str(e)}"