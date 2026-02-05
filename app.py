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
# Nieuw formaat: "Naam": ["TICKER", Aantal, Inleg, "AANKOOPDATUM (YYYY-MM-DD)"]
# Als je de exacte datum niet weet, gok dan. 
# Zolang de datum maar VOOR 2026 ligt, berekent hij de YTD correct vanaf 1 jan.

portfolio = {
    "Argenx":          ["ARGX.BR", 1,   722.50,  "2024-05-10"],
    "ASML":            ["ASML.AS", 1,   691.18,  "2023-11-15"],
    "BNP Paribas":     ["BNP.PA",  3,   244.30,  "2024-01-01"],
    "CSG N.V.":        ["CSG.AS",  3,   106.36,  "2026-01-28"],
    "D'Ieteren":       ["DIE.BR",  2,   317.29,  "2026-01-12"],
    "Elia Group":      ["ELI.BR",  6,   516.73,  "2023-01-01"],
    "Gimv":            ["GIMB.BR", 5,   218.25,  "2022-01-01"],
    "GBL":             ["GBLB.BR", 4,   290.29,  "2024-01-01"],
    "Novo Nordisk":    ["NOVO-B.CO", 7, 2957.76, "2023-08-20"], 
    "Alphabet":        ["GOOGL",   1,   335.54,  "2026-01-12"],
    "Denison Mines":   ["DNN",     100, 335.01,  "2026-01-08"],
    "Kodiak Robotics": ["KDK",     20,  188.35,  "2026-01-26"], # Voorbeeld: Stel dat je deze recent kocht?
    "Mitsui & Co":     ["MITSY",   1,   426.45,  "2024-01-01"],
    "iShares EMIM":    ["EMIM.AS", 10,  352.34,  "2024-01-01"],
    "Vanguard VWCE":   ["VWCE.DE", 5,   712.52,  "2023-01-01"],
    "WisdomTree Met":  ["WENH.DE", 20,  285.10,  "2026-02-09"],
}

def haal_data_op():
    totaal_inleg_eur = 0
    totaal_waarde_eur = 0
    totaal_waarde_ytd_start = 0
    
    # Huidig jaar bepalen voor de logica
    huidig_jaar = datetime.now().year
    
    # 1. Valuta ophalen
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
    tickers = [item[0] for item in portfolio.values()]
    data = yf.download(tickers, period="ytd", group_by='ticker', progress=False)
    
    for naam, info in portfolio.items():
        ticker, aantal, inleg_orig, datum_str = info
        
        try:
            if len(tickers) == 1:
                hist = data['Close']
            else:
                hist = data[ticker]['Close']
            
            clean_hist = hist.dropna()
            if clean_hist.empty: continue
            
            prijs_nu = float(clean_hist.iloc[-1])
            prijs_start_jaar = float(clean_hist.iloc[0])
            
            # --- Valuta Bepalen ---
            if ticker == "NOVO-B.CO":
                koers_nu = dkk_nu
                koers_start = dkk_start
            elif ticker in ["GOOGL", "DNN", "KDK", "MITSY"]:
                koers_nu = usd_nu
                koers_start = usd_start
            else:
                koers_nu = 1.0
                koers_start = 1.0
            
            # --- Huidige Waarde & Inleg ---
            waarde_nu_eur = (prijs_nu * aantal) / koers_nu
            inleg_eur = inleg_orig / koers_nu
            
            # --- YTD Logica (De Perfectie) ---
            # We kijken naar het aankoopjaar.
            datum_aankoop = datetime.strptime(datum_str, "%Y-%m-%d")
            
            if datum_aankoop.year == huidig_jaar:
                # Als je het DIT jaar kocht, is je "startwaarde" voor YTD gelijk aan wat je betaalde.
                # Want op 1 januari had je het nog niet.
                waarde_start_eur_item = inleg_eur 
            else:
                # Als je het vorig jaar al had, is de startwaarde de koers op 1 januari.
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
    
    waarde_nu, inleg, waarde_ytd_start = haal_data_op()
    
    # 1. Totaal Rendement (Huidig vs Inleg)
    if inleg > 0:
        rendement_totaal = ((waarde_nu - inleg) / inleg) * 100
        delta_totaal = waarde_nu - inleg
    else:
        rendement_totaal = 0
        delta_totaal = 0

    # 2. YTD Rendement (Huidig vs Startwaarde Jaar OF Aankoopwaarde)
    if waarde_ytd_start > 0:
        rendement_ytd = ((waarde_nu - waarde_ytd_start) / waarde_ytd_start) * 100
        delta_ytd = waarde_nu - waarde_ytd_start
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
