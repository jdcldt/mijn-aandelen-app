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

# --- JOUW PORTFOLIO ---
# Ik heb de tickers opgezocht en de prijs per aandeel berekend (Waarde / Aantal)
# CONTROLEER: Is 'koop_prijs' wat je BETAALD hebt? Of de huidige waarde?
# Pas aan indien nodig.

portfolio = {
    # 1. ASML Holding (Amsterdam)
    "ASML.AS": { "aantal": 1, "koop_prijs": 691.18, "valuta": "EUR" },

    # 2. Vanguard FTSE All-World (VWCE - Xetra Duitsland is meest gebruikt voor data)
    "VWCE.DE": { "aantal": 5, "koop_prijs": 142.50, "valuta": "EUR" }, # 738 / 5

    # 3. Elia Group (Brussel)
    "ELI.BR":  { "aantal": 6, "koop_prijs": 86.12, "valuta": "EUR" }, # 726 / 6

    # 4. Argenx (Brussel)
    "ARGX.BR": { "aantal": 1, "koop_prijs": 722.50, "valuta": "EUR" },

    # 5. Mitsui & Co ADR (USA - Dollar)
    "MIO.F":   { "aantal": 1, "koop_prijs": 426.45, "valuta": "USD" }, # Let op: is dit bedrag in € of $? Ik reken hier als $

    # 6. iShares EMIM (Amsterdam)
    "EMIM.AS": { "aantal": 10, "koop_prijs": 35.23, "valuta": "EUR" }, # 416 / 10

    # 7. D'Ieteren (Brussel)
    "DIE.BR":  { "aantal": 2, "koop_prijs": 158.65, "valuta": "EUR" }, # 390 / 2

    # 8. Denison Mines (USA - Dollar)
    "DNN":     { "aantal": 100, "koop_prijs": 3.35, "valuta": "USD" }, # 360 totaal. Prijs per stuk $3.60? 

    # 9. Novo Nordisk (Gebruik Duitse ticker in EUR voor gemak)
    "NOVA.DE": { "aantal": 7, "koop_prijs": 56.59, "valuta": "EUR" }, # 352 / 7

    # 10. GBL (Brussel)
    "GBLB.BR": { "aantal": 4, "koop_prijs": 72.57, "valuta": "EUR" }, # 319 / 4

    # 11. Alphabet / Google (USA - Dollar)
    "GOOGL":   { "aantal": 1, "koop_prijs": 335.54, "valuta": "USD" }, # Als je tabelwaarde €281 was, pas dit dan aan naar de Dollar prijs!

    # 12. BNP Paribas (Parijs)
    "BNP.PA":  { "aantal": 3, "koop_prijs": 81.43, "valuta": "EUR" }, # 272 / 3

    # 13. Gimv (Brussel)
    "GIMB.BR": { "aantal": 5, "koop_prijs": 43.65, "valuta": "EUR" }, # 230 / 5
    
    # 14. Kodiak Robotics (Waarschuwing: Is dit Kodiak Sciences? Robotics is vaak niet beursgenoteerd)
    "KDK":     { "aantal": 20, "koop_prijs": 9.42, "valuta": "USD" }, # 159 / 20

    # 15. CSG N.V. (Lastig te vinden, ik gok op CSG Systems of lokaal)
    "CSG.AS":  { "aantal": 3, "koop_prijs": 35.45, "valuta": "EUR" }, 

    # 16. WisdomTree Strategic Metals ETF
    "WENH.DE":  { "aantal": 20, "koop_prijs": 14.26, "valuta": "EUR" }, 
}

# --- DE LOGICA (Ongewijzigd) ---
def bereken_data():
    totaal_inleg = 0
    totaal_waarde_nu = 0
    totaal_waarde_jan1 = 0
    
    # 1. Haal USD koers op (History Year-to-Date)
    try:
        usd_hist = yf.Ticker("EURUSD=X").history(period="ytd")['Close']
        # Valuta nu en valuta op 1 jan (eerste handelsdag)
        usd_koers_nu = float(usd_hist.dropna().iloc[-1])
        usd_koers_start = float(usd_hist.dropna().iloc[0])
    except:
        usd_koers_nu = 1.08
        usd_koers_start = 1.08

    # 2. Haal alle koersen op (Period = YTD voor jaarstart en nu)
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
            
            # Schoon de data op (verwijder lege dagen)
            clean_hist = hist.dropna()
            
            if clean_hist.empty:
                continue

            prijs_nu = float(clean_hist.iloc[-1])   # Laatste koers
            prijs_start = float(clean_hist.iloc[0]) # Eerste koers van het jaar
            
            # Berekening (Houd rekening met KOD in dollars)
            if ticker == "KOD":
                waarde_nu_item = (prijs_nu * aantal) / usd_koers_nu
                waarde_start_item = (prijs_start * aantal) / usd_koers_start
            else:
                waarde_nu_item = prijs_nu * aantal
                waarde_start_item = prijs_start * aantal

            # Totalen optellen
            totaal_waarde_nu += waarde_nu_item
            totaal_waarde_jan1 += waarde_start_item
            totaal_inleg += inleg_item
            
        except:
            continue
            
    return totaal_waarde_nu, totaal_inleg, totaal_waarde_jan1

# --- WEERGAVE ---
try:
    waarde_nu, inleg, waarde_jan1 = bereken_data()
    
    # Berekening 1: Totaal Rendement (Sinds aankoop)
    if inleg > 0:
        rendement_totaal = ((waarde_nu - inleg) / inleg) * 100
    else:
        rendement_totaal = 0.0
        
    # Berekening 2: YTD Rendement (Sinds 1 jan)
    if waarde_jan1 > 0:
        rendement_ytd = ((waarde_nu - waarde_jan1) / waarde_jan1) * 100
    else:
        rendement_ytd = 0.0
    
    # Kleuren bepalen
    kleur_totaal = "#4CAF50" if rendement_totaal >= 0 else "#FF5252"
    teken_totaal = "+" if rendement_totaal >= 0 else ""
    
    kleur_ytd = "#4CAF50" if rendement_ytd >= 0 else "#FF5252"
    teken_ytd = "+" if rendement_ytd >= 0 else ""
    
    # De output
    st.markdown(
        f"""
        <div style="
            display: flex; 
            justify_content: center; 
            align_items: center; 
            height: 85vh; 
            flex-direction: column; 
            font-family: -apple-system, sans-serif;">
            
            <p style="font-size: 16px; color: gray; margin-bottom: 0px;">Totaal</p>
            <h1 style="font-size: 80px; margin: 0; line-height: 1.1; color: {kleur_totaal};">
                {teken_totaal}{rendement_totaal:.1f}%
            </h1>
            
            <div style="margin-top: 20px; text-align: center;">
                <p style="font-size: 16px; color: gray; margin-bottom: 0px;">YTD (Dit jaar)</p>
                <h2 style="font-size: 40px; margin: 0; color: {kleur_ytd};">
                    {teken_ytd}{rendement_ytd:.1f}%
                </h2>
            </div>

            <p style="font-size: 14px; color: #ccc; margin-top: 40px;">
                Waarde: €{int(waarde_nu)}
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if st.button('Verversen', type="primary", use_container_width=True):
        st.rerun()

except Exception as e:
    st.write(f"Data wordt geladen... ({e})")


