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

# --- PORTFOLIO (VOLLEDIG GEBASEERD OP JE CSV) ---
# Novo Nordisk en ASML zijn nu beide correct opgenomen met hun datums uit 2025.

portfolio = [
    # 1. Broadcom - 09-02-2026
    {"naam": "Broadcom", "ticker": "AVGO", "aantal": 1, "inleg": 342.76, "datum": "2026-02-09"}, # USD

    # 2. WisdomTree Metals - 02-02-2026
    {"naam": "WisdomTree Met", "ticker": "WENH.DE", "aantal": 20, "inleg": 290.20, "datum": "2026-02-02"}, 

    # 3. Vanguard VWCE (Deel 1) - 28-01-2026
    {"naam": "Vanguard VWCE", "ticker": "VWCE.DE", "aantal": 2, "inleg": 299.20, "datum": "2026-01-28"},

    # 4. Kodiak Robotics - 23-01-2026
    {"naam": "Kodiak Robotics", "ticker": "KDK", "aantal": 20, "inleg": 172.40, "datum": "2026-01-23"}, # USD

    # 5. Alphabet (Google) - 09-01-2026
    {"naam": "Alphabet", "ticker": "GOOGL", "aantal": 1, "inleg": 310.96, "datum": "2026-01-09"}, # USD

    # 6. D'Ieteren - 07-01-2026
    {"naam": "D'Ieteren", "ticker": "DIE.BR", "aantal": 2, "inleg": 398.00, "datum": "2026-01-07"},

    # 7. Denison Mines - 07-01-2026
    {"naam": "Denison Mines", "ticker": "DNN", "aantal": 100, "inleg": 396.00, "datum": "2026-01-07"}, # USD

    # 8. Argenx - 04-01-2026
    {"naam": "Argenx", "ticker": "ARGX.BR", "aantal": 1, "inleg": 706.60, "datum": "2026-01-04"},

    # 9. ASML Holding - 27-10-2025
    {"naam": "ASML", "ticker": "ASML.AS", "aantal": 1, "inleg": 691.18, "datum": "2025-10-27"},

    # 10. BNP Paribas - 27-07-2025
    {"naam": "BNP Paribas", "ticker": "BNP.PA", "aantal": 3, "inleg": 281.85, "datum": "2025-07-27"},

    # 11. Gimv - 24-07-2025
    {"naam": "Gimv", "ticker": "GIMB.BR", "aantal": 5, "inleg": 224.75, "datum": "2025-07-24"},

    # 12. iShares EMIM - 24-07-2025
    {"naam": "iShares EMIM", "ticker": "EMIM.AS", "aantal": 10, "inleg": 426.52, "datum": "2025-07-24"},

    # 13. Vanguard VWCE (Deel 2) - 22-07-2025
    {"naam": "Vanguard VWCE", "ticker": "VWCE.DE", "aantal": 3, "inleg": 448.80, "datum": "2025-07-22"},

    # 14. Elia Group (Deel 1) - 21-07-2025
    {"naam": "Elia Group", "ticker": "ELI.BR", "aantal": 1, "inleg": 126.90, "datum": "2025-07-21"},

    # 15. Novo Nordisk - 17-06-2025 (GEVONDEN: 7 stuks à 824,40 DKK)
    # Totaal inleg: 7 * 824.40 = 5770.80 DKK
    {"naam": "Novo Nordisk", "ticker": "NOVO-B.CO", "aantal": 7, "inleg": 5770.80, "datum": "2025-06-17"}, # DKK

    # 16. Mitsui & Co - 22-05-2025
    {"naam": "Mitsui & Co", "ticker": "MITSY", "aantal": 1, "inleg": 725.00, "datum": "2025-05-22"}, # USD

    # 17. GBL - 10-05-2025
    {"naam": "GBL", "ticker": "GBLB.BR", "aantal": 4, "inleg": 333.20, "datum": "2025-05-10"},

    # 18. Elia Group (Deel 2) - 15-11-2024 (Schatting o.b.v. 'oud bezit')
    {"naam": "Elia Group", "ticker": "ELI.BR", "aantal": 4, "inleg": 508.00, "datum": "2024-11-15"},

    # 19. Elia Group (Deel 3) - 01-01-2023 (Oud bezit)
    {"naam": "Elia Group", "ticker": "ELI.BR", "aantal": 1, "inleg": 86.00,  "datum": "2023-01-01"},
]

def haal_data_op():
    totaal_inleg_eur = 0
    totaal_waarde_eur = 0
    totaal_waarde_ytd_start = 0
    
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

    # 2. Unieke tickers downloaden
    unieke_tickers = list(set([item["ticker"] for item in portfolio]))
    data = yf.download(unieke_tickers, period="ytd", group_by='ticker', progress=False)
    
    # 3. Loop door alle transacties
    for transactie in portfolio:
        ticker = transactie["ticker"]
        aantal = transactie["aantal"]
        inleg_orig = transactie["inleg"]
        datum_str = transactie["datum"]
        
        try:
            if len(unieke_tickers) == 1:
                hist = data['Close']
            else:
                hist = data[ticker]['Close']
            
            clean_hist = hist.dropna()
            if clean_hist.empty: continue
            
            prijs_nu = float(clean_hist.iloc[-1])
            prijs_start_jaar = float(clean_hist.iloc[0])
            
            # Valuta bepalen
            if ticker == "NOVO-B.CO":
                koers_nu = dkk_nu
                koers_start = dkk_start
            elif ticker in ["GOOGL", "DNN", "KDK", "MITSY", "AVGO"]:
                koers_nu = usd_nu
                koers_start = usd_start
            else:
                koers_nu = 1.0
                koers_start = 1.0
            
            # Waarde & Inleg
            waarde_nu_eur = (prijs_nu * aantal) / koers_nu
            inleg_eur = inleg_orig / koers_nu
            
            # YTD Logica
            datum_aankoop = datetime.strptime(datum_str, "%Y-%m-%d")
            
            if datum_aankoop.year == huidig_jaar:
                waarde_start_eur_item = inleg_eur 
            else:
                waarde_start_eur_item = (prijs_start_jaar * aantal) / koers_start

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
    
    # 1. Totaal Rendement
    if inleg > 0:
        rendement_totaal = ((waarde_nu - inleg) / inleg) * 100
        delta_totaal = waarde_nu - inleg
    else:
        rendement_totaal = 0
        delta_totaal = 0

    # 2. YTD Rendement
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
