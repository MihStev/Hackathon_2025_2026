import os
from dotenv import load_dotenv
from mock_apis import (
    get_booked_transactions,
    get_neplacene_fakture,
    get_account,
    get_efakture,
)
from db_manager import (
    get_ukupna_masa_plata,
    get_mesecni_fiksni_troskovi,
    get_fiksni_troskovi_po_kategoriji,
    get_zaposleni_po_sektoru,
)

load_dotenv()

# ── Routing tabela — specifičniji pre opštijih ──
ROUTES = [
    (["neplaćen", "neplacen", "dospel", "kasni"],           "neplacene_fakture"),
    (["faktura", "efaktura", "fakture"],                     "fakture"),
    (["fiksni trošak", "fiksni trosak", "fiksni"],           "fiksni_troskovi"),
    (["plata", "plate", "zaposleni", "zaposlena", "sektor"], "zaposleni"),
    (["transakcij", "banka", "uplata", "isplata", "prihod", "rashod"], "transakcije"),
    (["stanje", "račun", "racun", "balans", "saldo"],        "racun"),
]


def _route(upit: str) -> str:
    upit_lower = upit.lower()
    for kljucevi, ruta in ROUTES:
        if any(k in upit_lower for k in kljucevi):
            return ruta
    return "opste"


# ── Handleri ──

def _handle_neplacene_fakture() -> str:
    fakture = get_neplacene_fakture()
    if not fakture:
        return "✅ Sve fakture su plaćene. Nema dospelih obaveza."
    linije = ["⚠️ **Neplaćene / dospele fakture:**\n"]
    ukupno = 0.0
    for f in fakture:
        iznos = float(f["invoiceAmount"]["payableAmount"])
        ukupno += iznos
        linije.append(
            f"• **{f['buyer']['name']}** — {iznos:,.2f} RSD "
            f"| Status: {f['status']} "
            f"| Rok: {f['paymentDueDate']}"
        )
    linije.append(f"\n💰 Ukupno dugovanje: **{ukupno:,.2f} RSD**")
    return "\n".join(linije)


def _handle_fakture() -> str:
    fakture = get_efakture()["data"]["invoices"]
    placene  = sum(1 for f in fakture if f["status"] == "Approved")
    neplacene = len(fakture) - placene
    ukupno   = sum(float(f["invoiceAmount"]["payableAmount"]) for f in fakture)
    return (
        f"📄 **Pregled eFaktura**\n\n"
        f"• Ukupno faktura: {len(fakture)}\n"
        f"• Plaćene: {placene}\n"
        f"• Neplaćene / na čekanju: {neplacene}\n"
        f"• Ukupna vrednost: **{ukupno:,.2f} RSD**\n\n"
        f"Pitaj me za 'neplaćene fakture' da vidiš detalje."
    )


def _handle_fiksni_troskovi() -> str:
    mesecni = get_mesecni_fiksni_troskovi()
    po_kat  = get_fiksni_troskovi_po_kategoriji()
    linije  = [f"🏢 **Fiksni troškovi — mesečno: {mesecni:,.2f} RSD**\n"]
    linije.append("Po kategoriji:")
    for kat, iznos in po_kat:
        linije.append(f"  • {kat}: {iznos:,.2f} RSD")
    return "\n".join(linije)


def _handle_zaposleni() -> str:
    masa      = get_ukupna_masa_plata()
    po_sektoru = get_zaposleni_po_sektoru()
    linije    = [f"👥 **Masa plata — mesečno: {masa:,.2f} RSD**\n"]
    linije.append("Zaposleni po sektoru:")
    for sektor, broj, ukupno in po_sektoru:
        linije.append(f"  • {sektor}: {broj} zaposlenih | {ukupno:,.2f} RSD")
    return "\n".join(linije)


def _handle_transakcije() -> str:
    transakcije = get_booked_transactions()
    prihodi = sum(float(t["transactionAmount"]["amount"]) for t in transakcije if float(t["transactionAmount"]["amount"]) > 0)
    rashodi = sum(float(t["transactionAmount"]["amount"]) for t in transakcije if float(t["transactionAmount"]["amount"]) < 0)
    return (
        f"🏦 **Bankovne transakcije (poslednja 3 meseca)**\n\n"
        f"• Broj transakcija: {len(transakcije)}\n"
        f"• Ukupni prihodi: **{prihodi:,.2f} RSD**\n"
        f"• Ukupni rashodi: **{abs(rashodi):,.2f} RSD**\n"
        f"• Neto: **{prihodi + rashodi:,.2f} RSD**"
    )


def _handle_racun() -> str:
    data = get_account()
    acc  = data["data"]["account"]
    bal  = data["data"]["balances"][0]["balanceAmount"]
    return (
        f"💳 **Stanje računa**\n\n"
        f"• IBAN: `{acc['iban']}`\n"
        f"• Tip: {acc['cashAccountType']}\n"
        f"• Status: {acc['status']}\n"
        f"• Trenutno stanje: **{float(bal['amount']):,.2f} {bal['currency']}**"
    )


def _handle_opste(upit: str) -> str:
    return (
        "🤖 Mogu da ti pomognem sa sledećim pitanjima:\n\n"
        "• **Stanje računa** — trenutni saldo\n"
        "• **Transakcije** — prihodi i rashodi iz banke\n"
        "• **Fakture** — pregled svih eFaktura\n"
        "• **Neplaćene fakture** — upozorenja i dugovanja\n"
        "• **Fiksni troškovi** — mesečne obaveze po kategoriji\n"
        "• **Zaposleni / plate** — masa plata po sektoru\n\n"
        "Probaj neko od ovih pitanja!"
    )


# ── Entry point ──

def odgovori(upit: str) -> str:
    ruta = _route(upit)
    handlers = {
        "neplacene_fakture": _handle_neplacene_fakture,
        "fakture":           _handle_fakture,
        "fiksni_troskovi":   _handle_fiksni_troskovi,
        "zaposleni":         _handle_zaposleni,
        "transakcije":       _handle_transakcije,
        "racun":             _handle_racun,
        "opste":             lambda: _handle_opste(upit),
    }
    return handlers[ruta]()


if __name__ == "__main__":
    test_upiti = [
        "Kakvo je stanje na računu?",
        "Prikaži mi transakcije iz banke",
        "Koje fakture nisu plaćene?",
        "Koliki su fiksni troškovi?",
        "Koliko imam zaposlenih?",
        "Šta umeš da radiš?",
    ]
    for upit in test_upiti:
        print(f"\n{'─'*50}")
        print(f"❓ {upit}")
        print(odgovori(upit))