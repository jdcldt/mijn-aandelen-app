import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURATIE ---
st.set_page_config(page_title="Mijn Portfolio", layout="centered")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- PORTFOLIO (GEBASEERD OP JOUW SPREADSHEET) ---
# Structuur: "Naam": ["TICKER", Aantal, Totale_Inleg_In_Oorspronkelijke_Valuta]
portfolio = {
    "Argenx":         ["ARGX.BR", 1,   722.50],  # EUR
    "ASML":           ["ASML.AS", 1,   691.18],  # EUR
    "BNP Paribas":    ["BNP.PA",  3,   244.30],  # EUR (3 * 81.43)
    "CSG N.V.":       ["CSG.AS",  3,   106.36],  # EUR (3 * 35.45)
    "D'Ieteren":      ["DIE.BR",  2,   317.29],  # EUR (2 * 158.64)
    "Elia Group":     ["ELI.BR",  6,   516.73],  # EUR (6 * 86.12)
    "Gimv":           ["GIMB.BR", 5,   218.25],  # EUR (5 * 43.65)
    "GBL":            ["GBLB.BR", 4,   290.29],  # EUR (4 * 72.57)
    "Novo Nordisk":   ["NOVO-B.CO", 7, 2957.76], # DKK (Totale inleg in Kronen)
    "Alphabet":       ["GOOGL",   1,   335.54],  # USD
    "Denison Mines":  ["DNN",     100, 335.01],  # USD (100 * 3.35)
    "Kodiak Robotics":["KDK",     20,  188.35],  # USD (20 * 9.41)
    "Mitsui & Co":    ["MITSY",   1,   426.45],  # USD
    "iShares EMIM":   ["EMIM.AS", 10,  352.34],  # EUR (10 * 35.23)
    "Vanguard VWCE":  ["VWCE.DE", 5,   712.52],  # EUR (5 * 142.50)
    "WisdomTree Met": ["WENH.DE", 20,  285.10],  # EUR (20 * 14.25)
}

def bereken_data():
    totaal_inleg = 0
    totaal_waarde_nu = 0
    totaal_waarde_jan1 = 0
    
    # 1. Haal Valuta Koersen op (USD en DKK)
    # We halen op hoeveel de vreemde munt waard is in Euro (koers inverse van EURUSD=X)
    # EURUSD=X betekent: 1 Euro = 1.08 USD. Dus delen we door deze koers.
    try:
        usd_hist = yf.Ticker("EURUSD=X").history(period="ytd")['Close']
        usd_koers_nu = float(usd_hist.dropna().iloc[-1])
        usd_koers_start = float(usd_hist.dropna().iloc[0])
    except:
        usd_koers_nu = 1.08
        usd_koers_start = 1.08

    try:
        dkk_hist = yf.Ticker("EURDKK=X").history(period="ytd")['Close']
        dkk_koers_nu = float(dkk_hist.dropna().iloc[-1])
        dkk_koers_start = float(dkk_hist.dropna().iloc[0])
    except:
        dkk_koers_nu = 7.46
        dkk_koers_start = 7.46

    # 2. Haal alle koersen op
    tickers = [item[0] for item in portfolio.values()]
    data = yf.download(tickers, period="ytd", group_by='ticker', progress=False)
    
    for naam, info in portfolio.items():
        ticker, aantal, inleg_item = info
        
        try:
            # Data extractie
            if len(tickers) == 1:
                hist = data['Close']
            else:
                hist = data[ticker]['Close']
            
            clean_hist = hist.dropna()
            if clean_hist.empty: continue

            prijs_nu = float(clean_hist.iloc[-1])
            prijs_start = float(clean_hist.iloc[0])
            
            # --- VALUTA CONVERSIE ---
            # Bepaal de wisselkoers op basis van de ticker/munt
            if ticker == "NOVO-B.CO": # Deense Kroon
                koers_nu = dkk_koers_nu
                koers_start = dkk_koers_start
            elif ticker in ["GOOGL", "DNN", "KDK", "MITSY"]: # US Dollar
                koers_nu = usd_koers_nu
                koers_start = usd_koers_start
            else: # Euro (Geen conversie nodig, deler is 1)
                koers_nu = 1.0
                koers_start = 1.0

            # Berekening in Euro's (Waarde / Wisselkoers)
            waarde_nu_item = (prijs_nu * aantal) / koers_nu
            waarde_start_item = (prijs_start * aantal) / koers_start
            
            # De inleg is vast in de oorspronkelijke valuta, dus die rekenen we om met de HUIDIGE koers
            # (Of je historische koers wilt gebruiken is een keuze, hier gebruiken we actuele waarde vs actuele inleg-waarde)
            inleg_item_eur = inleg_item / koers_nu

            totaal_waarde_nu += waarde_nu_item
            totaal_waarde_jan1 += waarde_start_item
            totaal_inleg += inleg_item_eur
            
        except:
            continue
            
    return totaal_waarde_nu, totaal_inleg, totaal_waarde_jan1

# --- WEERGAVE ---
try:
    waarde_nu, inleg, waarde_jan1 = bereken_data()
    
    # Rendement Totaal
    if inleg > 0:
        rendement_totaal = ((waarde_nu - inleg) / inleg) * 100
    else:
        rendement_totaal = 0.0
        
    # Rendement YTD
    if waarde_jan1 > 0:
        rendement_ytd = ((waarde_nu - waarde_jan1) / waarde_jan1) * 100
    else:
        rendement_ytd = 0.0
    
    kleur_totaal = "#4CAF50" if rendement_totaal >= 0 else "#FF5252"
    teken_totaal = "+" if rendement_totaal >= 0 else ""
    
    kleur_ytd = "#4CAF50" if rendement_ytd >= 0 else "#FF5252"
    teken_ytd = "+" if rendement_ytd >= 0 else ""
    
    st.markdown(
        f"""
        <div style="
            display: flex; 
            justify_content: center; 
            align_items: center; 
            height: 85vh; 
            flex-direction: column; 
            font-family: -apple-system, sans-serif;">
            
            <p style="font-size: 16px; color: gray; margin-bottom: 0px;">Totaal Rendement</p>
            <h1 style="font-size: 80px; margin: 0; line-height: 1.1; color: {kleur_totaal};">
                {teken_totaal}{rendement_totaal:.1f}%
            </h1>
            
            <div style="margin-top: 30px; text-align: center;">
                <p style="font-size: 16px; color: gray; margin-bottom: 0px;">YTD (2026)</p>
                <h2 style="font-size: 40px; margin: 0; color: {kleur_ytd};">
                    {teken_ytd}{rendement_ytd:.1f}%
                </h2>
            </div>

            <p style="font-size: 14px; color: #ccc; margin-top: 40px;">
                Waarde: €{int(waarde_nu):,}
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if st.button('Verversen', type="primary", use_container_width=True):
        st.rerun()

except Exception as e:
    st.write(f"Bezig met laden... ({e})")
