import streamlit as st
import yfinance as yf

# --- CONFIGURATIE ---
st.set_page_config(page_title="Portfolio", layout="centered")

# Verberg standaard Streamlit elementen
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- JOUW PORTFOLIO ---
# Vul hier in: Ticker, Aantal, Gemiddelde aankoopprijs (in de valuta van het aandeel!), Valuta
portfolio = {
    "VWRL.AS": {
        "aantal": 50, 
        "koop_prijs": 94.50, 
        "valuta": "EUR"
    },
    "AAPL": {
        "aantal": 10, 
        "koop_prijs": 145.00, # Prijs in Dollars
        "valuta": "USD"
    },
    "MSFT": {
        "aantal": 5, 
        "koop_prijs": 280.00, # Prijs in Dollars
        "valuta": "USD"
    }
}

# --- DE LOGICA ---
def bereken_rendement():
    totaal_inleg_eur = 0
    huidige_waarde_eur = 0
    
    # 1. Haal de wisselkoers op (EUR/USD)
    # We halen op hoeveel Dollar 1 Euro waard is (bijv 1.08)
    try:
        valuta_data = yf.Ticker("EURUSD=X").history(period="5d")['Close'].iloc[-1]
        eur_usd_koers = float(valuta_data)
    except:
        eur_usd_koers = 1.08 # Fallback als yahoo faalt

    # 2. Haal aandelenkoersen op
    tickers = list(portfolio.keys())
    # We downloaden alles in één keer voor snelheid
    data = yf.download(tickers, period="5d", progress=False)['Close']

    for ticker, info in portfolio.items():
        # Huidige prijs ophalen uit de download
        if len(tickers) == 1:
            live_prijs = float(data.iloc[-1])
        else:
            live_prijs = float(data[ticker].iloc[-1])
            
        aantal = info['aantal']
        koop_prijs = info['koop_prijs']
        valuta = info['valuta']

        # --- CONVERSIE NAAR EURO ---
        if valuta == "USD":
            # Omrekenen: Bedrag in Dollar / Koers (bijv 150 / 1.08 = 138 Euro)
            huidige_waarde_positie = (live_prijs * aantal) / eur_usd_koers
            
            # LET OP: We rekenen de inleg ook om tegen de HUIDIGE koers. 
            # Dit toont puur de winst van het aandeel, en negeert valuta-winst/verlies op je inleg.
            # Wil je valuta-winst op inleg mee rekenen? Dan moet je hier de historische koers gebruiken.
            inleg_positie = (koop_prijs * aantal) / eur_usd_koers
            
        else:
            # Gewoon Euro
            huidige_waarde_positie = live_prijs * aantal
            inleg_positie = koop_prijs * aantal

        huidige_waarde_eur += huidige_waarde_positie
        totaal_inleg_eur += inleg_positie

    # Totaal percentage
    if totaal_inleg_eur == 0:
        return 0
    return ((huidige_waarde_eur - totaal_inleg_eur) / totaal_inleg_eur) * 100

# --- HET DASHBOARD ---
try:
    percentage = bereken_rendement()
    
    kleur = "#4CAF50" if percentage >= 0 else "#FF5252" # Groen of Rood
    teken = "+" if percentage >= 0 else ""
    
    st.markdown(
        f"""
        <div style="
            display: flex; 
            justify_content: center; 
            align_items: center; 
            height: 80vh; 
            flex-direction: column; 
            font-family: sans-serif;">
            <p style="font-size: 18px; color: gray; margin-bottom: 5px;">Portfolio Evolutie</p>
            <h1 style="font-size: 70px; margin: 0; color: {kleur};">
                {teken}{percentage:.2f}%
            </h1>
            <p style="font-size: 12px; color: #ccc; margin-top: 20px;">Live incl. wisselkoers</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if st.button('Verversen', type="primary", use_container_width=True):
        st.rerun()

except Exception as e:

    st.error(f"Foutmelding: {e}")
