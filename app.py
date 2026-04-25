import streamlit as st
from mock_apis import get_account, get_booked_transactions, get_efakture
from db_manager import get_ukupna_masa_plata, get_mesecni_fiksni_troskovi, init_db
from ai_agent import odgovori
import pandas as pd

st.set_page_config(
    page_title="FinAssist AI",
    page_icon="💼",
    layout="wide",
)

init_db()

@st.cache_data(ttl=60)
def ucitaj_podatke():
    account_data = get_account()
    transakcije  = get_booked_transactions()
    efakture_raw = get_efakture()["data"]["invoices"]
    return account_data, transakcije, efakture_raw

account_data, transakcije, efakture = ucitaj_podatke()

# ── Konverzija u float (mock vraća stringove) ──
saldo     = float(account_data["data"]["balances"][0]["balanceAmount"]["amount"])
prihodi   = sum(float(t["transactionAmount"]["amount"]) for t in transakcije if float(t["transactionAmount"]["amount"]) > 0)
rashodi   = sum(float(t["transactionAmount"]["amount"]) for t in transakcije if float(t["transactionAmount"]["amount"]) < 0)
neplacene = [f for f in efakture if f["status"] != "Approved"]
dugovanje = sum(float(f["invoiceAmount"]["payableAmount"]) for f in neplacene)

# ─────────────────────────────────────────────
st.title("💼 FinAssist AI")
st.caption("Vaš finansijski asistent — sve na jednom mestu")
st.divider()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💳 Stanje računa",     f"{saldo:,.0f} RSD")
k2.metric("📈 Prihodi (3m)",      f"{prihodi:,.0f} RSD")
k3.metric("📉 Rashodi (3m)",      f"{abs(rashodi):,.0f} RSD")
k4.metric("👥 Masa plata",        f"{get_ukupna_masa_plata():,.0f} RSD / mes")
k5.metric("⚠️ Neplaćene fakture", f"{len(neplacene)} kom",
          delta=f"-{dugovanje:,.0f} RSD",
          delta_color="inverse")

st.divider()

# ── Cash Flow grafikon ──
st.subheader("📊 Cash Flow — poslednja 3 meseca")

df = pd.DataFrame([
    {
        "Datum":      t["bookingDate"],
        "Iznos":      float(t["transactionAmount"]["amount"]),
        "Opis":       t.get("remittanceInformationUnstructured", ""),
        "Kategorija": t.get("bankTransactionCode", ""),
    }
    for t in transakcije
])

df["Datum"]     = pd.to_datetime(df["Datum"])
df["Mesec"]     = df["Datum"].dt.to_period("M").astype(str)
df["Tip"]       = df["Iznos"].apply(lambda x: "Prihod" if x > 0 else "Rashod")
df["Iznos_abs"] = df["Iznos"].abs()

mesecni = df.groupby(["Mesec", "Tip"])["Iznos_abs"].sum().reset_index()
pivot   = mesecni.pivot(index="Mesec", columns="Tip", values="Iznos_abs").fillna(0)

st.bar_chart(pivot, color=["#ef4444", "#22c55e"])

# ── Tabele ──
tab1, tab2 = st.tabs(["🏦 Transakcije", "📄 eFakture"])

with tab1:
    prikaz = df[["Datum", "Opis", "Kategorija", "Iznos"]].copy()
    prikaz["Datum"] = prikaz["Datum"].dt.strftime("%d.%m.%Y.")
    prikaz["Iznos"] = prikaz["Iznos"].apply(
        lambda x: f"+{x:,.2f} RSD" if x > 0 else f"{x:,.2f} RSD"
    )
    st.dataframe(prikaz, use_container_width=True, hide_index=True)

with tab2:
    efak_prikaz = pd.DataFrame([
        {
            "Broj fakture": f["invoiceId"],
            "Kupac":        f["buyer"]["name"],
            "Iznos (RSD)":  f"{float(f['invoiceAmount']['payableAmount']):,.2f}",
            "Status":       f["status"],
            "Rok plaćanja": f["paymentDueDate"],
        }
        for f in efakture
    ])

    def obradi_status(s):
        if s == "Approved": return "✅ Plaćeno"
        if s == "Sent":     return "🟡 Poslato"
        if s == "Sending":  return "🟠 U slanju"
        return "🔴 " + s

    efak_prikaz["Status"] = efak_prikaz["Status"].apply(obradi_status)
    st.dataframe(efak_prikaz, use_container_width=True, hide_index=True)

st.divider()

# ── AI Chat ──
st.subheader("🤖 Razgovaraj sa FinAssist AI")

if "poruke" not in st.session_state:
    st.session_state.poruke = [
        {
            "role":    "assistant",
            "content": "👋 Zdravo! Ja sam FinAssist AI. Pitajte me o vašim finansijama — stanje računa, transakcije, fakture, troškovi ili plate.",
        }
    ]

for poruka in st.session_state.poruke:
    with st.chat_message(poruka["role"]):
        st.markdown(poruka["content"])

upit = st.chat_input("Npr: Koje fakture nisu plaćene?")
if upit:
    st.session_state.poruke.append({"role": "user", "content": upit})
    with st.chat_message("user"):
        st.markdown(upit)

    with st.chat_message("assistant"):
        with st.spinner("Analiziram..."):
            odgovor = odgovori(upit)
        st.markdown(odgovor)

    st.session_state.poruke.append({"role": "assistant", "content": odgovor})