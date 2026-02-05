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
    "MITSY":   { "aantal": 1, "koop_prijs": 426.45, "valuta": "USD" }, # Let op: is dit bedrag in € of $? Ik reken hier als $

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
def bereken_rendement():
    totaal_inleg_eur = 0
    huidige_waarde_eur = 0
    
    try:
        valuta_hist = yf.Ticker("EURUSD=X").history(period="5d")
        eur_usd_koers = float(valuta_hist['Close'].dropna().iloc[-1])
    except:
        eur_usd_koers = 1.08 

    tickers = list(portfolio.keys())
    if not tickers: return 0
    
    raw_data = yf.download(tickers, period="5d", group_by='ticker', progress=False)

    for ticker, info in portfolio.items():
        try:
            if len(tickers) == 1:
                hist_data = raw_data['Close']
            else:
                hist_data = raw_data[ticker]['Close']
            
            live_prijs = float(hist_data.dropna().iloc[-1])
            
            aantal = info['aantal']
            koop_prijs = info['koop_prijs']
            valuta = info['valuta']

            if valuta == "USD":
                huidige_waarde_positie = (live_prijs * aantal) / eur_usd_koers
                inleg_positie = (koop_prijs * aantal) / eur_usd_koers
            else:
                huidige_waarde_positie = live_prijs * aantal
                inleg_positie = koop_prijs * aantal

            huidige_waarde_eur += huidige_waarde_positie
            totaal_inleg_eur += inleg_positie
            
        except Exception as e:
            continue

    if totaal_inleg_eur == 0: return 0
    return ((huidige_waarde_eur - totaal_inleg_eur) / totaal_inleg_eur) * 100

# --- DASHBOARD ---
try:
    percentage = bereken_rendement()
    kleur = "#4CAF50" if percentage >= 0 else "#FF5252"
    teken = "+" if percentage >= 0 else ""
    
    st.markdown(
        f"""
        <div style="display: flex; justify_content: center; align_items: center; height: 80vh; flex-direction: column; font-family: sans-serif;">
            <p style="font-size: 18px; color: gray; margin-bottom: 5px;">Portfolio Evolutie</p>
            <h1 style="font-size: 70px; margin: 0; color: {kleur};">
                {teken}{percentage:.2f}%
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    if st.button('Verversen', type="primary", use_container_width=True):
        st.rerun()

except Exception as e:
    st.error(f"Er ging iets mis: {e}")
