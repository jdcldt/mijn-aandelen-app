import streamlit as st
import yfinance as yf

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
# AANGEPAST: Kodiak Robotics heeft nu de juiste ticker 'KDK' (Nasdaq).
portfolio = {
    "Argenx":          ["ARGX.BR", 1,   722.50],
    "ASML":            ["ASML.AS", 1,   691.18],
    "BNP Paribas":     ["BNP.PA",  3,   244.30],
    "CSG N.V.":        ["CSG.AS",  3,   106.36],
    "D'Ieteren":       ["DIE.BR",  2,   317.29],
    "Elia Group":      ["ELI.BR",  6,   516.73],
    "Gimv":            ["GIMB.BR", 5,   218.25],
    "GBL":             ["GBLB.BR", 4,   290.29],
    "Novo Nordisk":    ["NOVO-B.CO", 7, 2957.76], # DKK
    "Alphabet":        ["GOOGL",   1,   335.54],  # USD
    "Denison Mines":   ["DNN",     100, 335.01],  # USD
    "Kodiak Robotics": ["KDK",     20,  188.35],  # USD (Ticker KDK)
    "Mitsui & Co":     ["MITSY",   1,   426.45],  # USD
    "iShares EMIM":    ["EMIM.AS", 10,  352.34],
    "Vanguard VWCE":   ["VWCE.DE", 5,   712.52],
    "WisdomTree Met":  ["WENH.DE", 20,  285.10],
}

def haal_data_op():
    totaal_inleg_eur = 0
    totaal_waarde_eur = 0
    totaal_waarde_ytd = 0
    
    # 1. Valuta ophalen
    try:
        valuta_data = yf.download(["EURUSD=X", "EURDKK=X"], period="ytd", progress=False)['Close']
        
        # Laatste koersen
        usd_nu = float(valuta_data["EURUSD=X"].dropna().iloc[-1])
        dkk_nu = float(valuta_data["EURDKK=X"].dropna().iloc[-1])
        
        # Start koersen (1 jan)
        usd_start = float(valuta_data["EURUSD=X"].dropna().iloc[0])
        dkk_start = float(valuta_data["EURDKK=X"].dropna().iloc[0])
    except:
        usd_nu, usd_start = 1.08, 1.08
        dkk_nu, dkk_start = 7.46, 7.46

    # 2. Aandelen ophalen
    tickers = [item[0] for item in portfolio.values()]
    data = yf.download(tickers, period="ytd", group_by='ticker', progress=False)
    
    for naam, info in portfolio.items():
        ticker, aantal, inleg_orig = info
        
        try:
            if len(tickers) == 1:
                hist = data['Close']
            else:
                hist = data[ticker]['Close']
            
            clean_hist = hist.dropna()
            if clean_hist.empty: continue
            
            prijs_nu = float(clean_hist.iloc[-1])
            prijs_start = float(clean_hist.iloc[0])
            
            # --- Valuta Conversie ---
            # KDK is in dollars, dus valt onder de USD groep
            if ticker == "NOVO-B.CO":
                koers_nu = dkk_nu
                koers_start = dkk_start
            elif ticker in ["GOOGL", "DNN", "KDK", "MITSY"]:
                koers_nu = usd_nu
                koers_start = usd_start
            else:
                koers_nu = 1.0
                koers_start = 1.0
            
            # Waarde berekenen
            waarde_nu_eur = (prijs_nu * aantal) / koers_nu
            waarde_start_eur = (prijs_start * aantal) / koers_start
            inleg_eur = inleg_orig / koers_nu

            totaal_waarde_eur += waarde_nu_eur
            totaal_waarde_ytd += waarde_start_eur
            totaal_inleg_eur += inleg_eur
            
        except:
            continue
            
    return totaal_waarde_eur, totaal_inleg_eur, totaal_waarde_ytd

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
            label="YTD (Dit jaar)",
            value=f"{rendement_ytd:.1f}%",
            delta=f"€{delta_ytd:,.0f}"
        )

    st.caption(f"Huidige waarde: €{waarde_nu:,.2f}")
    
    if st.button("Verversen"):
        st.rerun()

except Exception as e:
    st.error(f"Fout: {e}")
