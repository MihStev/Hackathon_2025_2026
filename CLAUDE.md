# O Projektu: FinAssist AI (Hackathon MVP)
Mi pravimo aplikaciju za kompanije gde se na jednom mestu vide svi finansijski podaci. Fokus je na MVP-u za hakaton. Aplikacija mora da radi brzo, bez komplikovanog deploymenta.

## Tech Stack
- Frontend: Streamlit (Python)
- Baza podataka: SQLite (lokalni fajl database.db)
- LLM Integracija: Google Cloud Vertex AI (vertexai paket) - za sad koristi mock odgovore dok ne dodamo API ključ.
- Backend/Podaci: Python skripte koje glume (mockuju) API-je.

## Arhitektura & Moduli
1. *Mock APIs (mock_apis.py)*: Funkcije koje vraćaju lažne JSON podatke za Banku (transakcije) i eFakture.
2. *Database (db_manager.py)*: Skripta za kreiranje SQLite baze (Zaposleni, Fiksni_Troskovi) i pisanje/čitanje iz nje.
3. *AI Logic (ai_agent.py)*: Logika koja prima upit, odlučuje da li da vuče iz baze, mock API-ja, ili da odgovori na opšte pitanje.
4. *App (app.py)*: Streamlit dashboard koji prikazuje grafikone (Cash flow) i UI za chat.

## Pravila za pisanje koda (Claude Skills)
- *KISS (Keep It Simple, Stupid)*: Ovo je hakaton. Ne pravi složene klase i arhitekture. Koristi jednostavne funkcije.
- *Mockuj pametno*: Generiši smislene test podatke na srpskom jeziku (imena srpskih firmi, valuta RSD, realni iznosi).
- *Function Calling*: Kada praviš AI agenta, napravi lokalne Python funkcije koje AI može da pozove.
- *Bezbednost*: Svi API ključevi moraju da se vuku iz .env fajla (koristi python-dotenv). Nikada nemoj hardkodirati ključeve.
- Pre nego što instaliraš bilo koji paket, pitaj za dozvolu i dodaj ga u requirements.txt.
