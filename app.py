import streamlit as st
import yfinance as yf
from datetime import datetime

# --- CONFIGURATIE ---
st.set_page_config(page_title="Portfolio", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- PORTFOLIO ---
# Inleg is nu exact overgenomen uit je 'Portfolio Snapshot' (05-02) 
# + 'Orderhistoriek' (voor recente wijzigingen).

portfolio = [
    # 1. Broadcom (AVGO) - Aankoop 09-02-2026 (Uit PDF)
    # 1 aandeel. Totale kosten uit PDF: 293.92 EUR.
    # Omdat we de EUR kosten weten, zetten we 'valuta_override' op True.
    {"naam": "Broadcom", "ticker": "AVGO", "aantal": 1, "inleg": 293.92, "valuta": "EUR", "datum": "2026-02-09"},

    # 2. Vanguard VWCE - Totaal 5 stuks. Snapshot waarde: 712.52 EUR.
    # Deel 1: 2 stuks gekocht jan 2026 voor 299.20 EUR (Uit PDF).
    {"naam": "Vanguard VWCE", "ticker": "VWCE.DE", "aantal": 2, "inleg": 299.20, "valuta": "EUR", "datum": "2026-01-28"},
    # Deel 2: De overige 3 stuks (Restant van 712.52 - 299.20 = 413.32)
    {"naam": "Vanguard VWCE", "ticker": "VWCE.DE", "aantal": 3, "inleg": 413.32, "valuta": "EUR", "datum": "2025-07-22"},

    # 3. WisdomTree Metals - 20 stuks. Snapshot: 285.10 EUR. (PDF zei 287, we pakken snapshot voor consistentie met bank)
    {"naam": "WisdomTree Met", "ticker": "WENH.DE", "aantal": 20, "inleg": 285.10, "valuta": "EUR", "datum": "2026-02-02"},

    # 4. Kodiak Robotics - 20 stuks. Snapshot: 188.35 USD.
    {"naam": "Kodiak Robotics", "ticker": "KDK", "aantal": 20, "inleg": 188.35, "valuta": "USD", "datum": "2026-01-23"},

    # 5. Alphabet - 1 stuk. Snapshot: 335.54 USD.
    {"naam": "Alphabet", "ticker": "GOOGL", "aantal": 1, "inleg": 335.54, "valuta": "USD", "datum": "2026-01-09"},

    # 6. D'Ieteren - 2 stuks. Snapshot: 317.29 EUR. (Gemiddeld 158.64)
    {"naam": "D'Ieteren", "ticker": "DIE.BR", "aantal": 2, "inleg": 317.29, "valuta": "EUR", "datum": "2026-01-07"},

    # 7. Denison Mines - 100 stuks. Snapshot: 335.01 USD. (Gemiddeld 3.35)
    {"naam": "Denison Mines", "ticker": "DNN", "aantal": 100, "inleg": 335.01, "valuta": "USD", "datum": "2026-01-07"},

    # 8. Argenx - 1 stuk. Snapshot: 722.50 EUR.
    {"naam": "Argenx", "ticker": "ARGX.BR", "aantal": 1, "inleg": 722.50, "valuta": "EUR", "datum": "2026-01-04"},

    # 9. ASML - 1 stuk. Snapshot: 691.18 EUR.
    {"naam": "ASML", "ticker": "ASML.AS", "aantal": 1, "inleg": 691.18, "valuta": "EUR", "datum": "2025-10-27"},

    # 10. BNP Paribas - 3 stuks. Snapshot: 244.30 EUR. (Gem 81.43)
    {"naam": "BNP Paribas", "ticker": "BNP.PA", "aantal": 3, "inleg": 244.30, "valuta": "EUR", "datum": "2025-07-27"},

    # 11. Gimv - 5 stuks. Snapshot: 218.25 EUR.
    {"naam": "Gimv", "ticker": "GIMB.BR", "aantal": 5, "inleg": 218.25, "valuta": "EUR", "datum": "2025-07-24"},

    # 12. iShares EMIM - 10 stuks. Snapshot: 352.34 EUR.
    {"naam": "iShares EMIM", "ticker": "EMIM.AS", "aantal": 10, "inleg": 352.34, "valuta": "EUR", "datum": "2025-07-24"},

    # 13. Elia Group - 6 stuks. Snapshot: 516.73 EUR. (Gem 86.12)
    # Aangezien niet in recente historie, zetten we datum op 'oud' (2024).
    {"naam": "Elia Group", "ticker": "ELI.BR", "aantal": 6, "inleg": 516.73, "valuta": "EUR", "datum": "2024-01-01"},

    # 14. Mitsui & Co - 1 stuk. Snapshot: 426.45 USD.
    {"naam": "Mitsui & Co", "ticker": "MITSY", "aantal": 1, "inleg": 426.45, "valuta": "USD", "datum": "2025-05-22"},

    # 15. GBL - 4 stuks. Snapshot: 290.29 EUR. (Gem 72.57)
    {"naam": "GBL", "ticker": "GBLB.BR", "aantal": 4, "inleg": 290.29, "valuta": "EUR", "datum": "2025-05-10"},

    # 16. Novo Nordisk - 7 stuks. Snapshot: 2957.76 DKK.
    {"naam": "Novo Nordisk", "ticker": "NOVO-B.CO", "aantal": 7, "inleg": 2957.76, "valuta": "DKK", "datum": "2025-06-17"},
]

def haal_data_op():
    totaal_inleg_eur = 0
    totaal_waarde_eur = 0
    totaal_waarde_ytd_start = 0
    
    huidig_jaar = datetime.now().year
    
    # 1. Valuta ophalen (USD en DKK)
    try:
        valuta_data = yf.download(["EURUSD=X", "EURDKK=X"], period="ytd", progress=False)['Close']
        usd_nu = float(valuta_data["EURUSD=X"].dropna().iloc[-1])
        dkk_nu = float(valuta_data["EURDKK=X"].dropna().iloc[-1])
        usd_start = float(valuta_data["EURUSD=X"].dropna().iloc[0])
        dkk_start = float(valuta_data["EURDKK=X"].dropna().iloc[0])
    except:
        usd_nu, usd_start = 1.08, 1.08
        dkk_nu, dkk_start = 7.46, 7.46

    # 2. Aandelen ophalen
    unieke_tickers = list(set([item["ticker"] for item in portfolio]))
    data = yf.download(unieke_tickers, period="ytd", group_by='ticker', progress=False)
    
    for item in portfolio:
        ticker = item["ticker"]
        aantal = item["aantal"]
        inleg_orig = item["inleg"]
        valuta = item["valuta"]
        datum_str = item["datum"]
        
        try:
            # Data selectie
            if len(unieke_tickers) == 1:
                hist = data['Close']
            else:
                hist = data[ticker]['Close']
            
            clean_hist = hist.dropna()
            if clean_hist.empty: continue
            
            prijs_nu = float(clean_hist.iloc[-1])
            prijs_start_jaar = float(clean_hist.iloc[0])
            
            # Wisselkoersen bepalen
            if valuta == "DKK":
                koers_nu = dkk_nu
                koers_start = dkk_start
                historische_koers_inleg = 7.46 # Vaste koers voor inleg (schatting)
            elif valuta == "USD":
                koers_nu = usd_nu
                koers_start = usd_start
                historische_koers_inleg = 1.09 # Vaste koers voor inleg (schatting 2026)
            else: # EUR
                koers_nu = 1.0
                koers_start = 1.0
                historische_koers_inleg = 1.0

            # --- Huidige Waarde ---
            waarde_nu_eur = (prijs_nu * aantal) / koers_nu
            
            # --- Inleg (Kostenbasis) ---
            # Als we de EUR kosten al weten (bijv Broadcom), gebruik die direct.
            # Anders rekenen we om. 
            # BELANGRIJK: We gebruiken een 'vaste' historische koers voor de inleg om valutawinst mee te tellen in het rendement.
            if valuta == "EUR":
                inleg_eur = inleg_orig
            else:
                # Hier gebruiken we de historische koers zodat je ook winst ziet als de dollar stijgt
                inleg_eur = inleg_orig / historische_koers_inleg

            # --- YTD Startwaarde ---
            datum_aankoop = datetime.strptime(datum_str, "%Y-%m-%d")
            
            if datum_aankoop.year == huidig_jaar:
                # Dit jaar gekocht? Startpunt = Je aankoopbedrag (in EUR op moment van aankoop)
                waarde_start_eur_item = inleg_eur 
            else:
                # Al in bezit? Startpunt = Waarde op 1 jan
                waarde_start_eur_item = (prijs_start_jaar * aantal) / koers_start

            # Totalen
            totaal_waarde_eur += waarde_nu_eur
            totaal_inleg_eur += inleg_eur
            totaal_waarde_ytd_start += waarde_start_eur_item
            
        except:
            continue
            
    return totaal_waarde_eur, totaal_inleg_eur, totaal_waarde_ytd_start

# --- DASHBOARD ---
try:
    st.title("Mijn Portfolio")
    
    waarde_nu, inleg, waarde_ytd = haal_data_op()
    
    if inleg > 0:
        rendement_totaal = ((waarde_nu - inleg) / inleg) * 100
        delta_totaal = waarde_nu - inleg
    else:
        rendement_totaal = 0
        delta_totaal = 0

    if waarde_ytd > 0:
        rendement_ytd = ((waarde_nu - waarde_ytd) / waarde_ytd) * 100
        delta_ytd = waarde_nu - waarde_ytd
    else:
        rendement_ytd = 0
        delta_ytd = 0

    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Totaal Rendement",
            value=f"{rendement_totaal:.1f}%",
            delta=f"€{delta_totaal:,.0f}"
        )
        
    with col2:
        st.metric(
            label=f"YTD ({datetime.now().year})",
            value=f"{rendement_ytd:.1f}%",
            delta=f"€{delta_ytd:,.0f}"
        )

    st.caption(f"Huidige waarde: €{waarde_nu:,.2f}")
    
    if st.button("Verversen"):
        st.rerun()

except Exception as e:
    st.error(f"Fout: {e}")
