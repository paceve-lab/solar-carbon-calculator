import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Carbon & Savings Calculator", layout="centered")

# ====================== CURRENCY CONFIGURATION ======================
st.sidebar.header("🌍 Currency Selection")

currency_options = {
    "USD - US Dollar": {"symbol": "$",   "code": "USD"},
    "EUR - Euro":      {"symbol": "€",   "code": "EUR"},
    "BRL - Brazilian Real": {"symbol": "R$", "code": "BRL"}
}

selected_currency_label = st.sidebar.selectbox(
    "Select display currency",
    options=list(currency_options.keys()),
    index=1  # Default: EUR (porque moras em Portugal)
)

selected_currency = currency_options[selected_currency_label]
symbol = selected_currency["symbol"]
currency_code = selected_currency["code"]

# Exchange rates (April 2026)
exchange_rates = {
    "USD": 5.15,
    "EUR": 1.0,      # Base para Portugal/Europa
    "BRL": 1.0
}

rate_to_base = exchange_rates[currency_code]   # Para EUR é 1.0

def format_currency(value_base: float) -> str:   # value_base agora em EUR
    if value_base is None or value_base < 0:
        value_base = 0.0
    converted = value_base / rate_to_base if currency_code != "EUR" else value_base
    return f"{symbol} {converted:,.2f}"

# ====================== SOLAR PRODUCTION DATA ======================
st.title("🌞 Solar Carbon & Savings Calculator")
st.markdown("**For Brazil and the Iberian Peninsula** | Updated 2026")

# Solar yield (kWh/kWp/year) - realistic averages
solar_yield = {
    # Brazil
    "Brazil - South": 1350,
    "Brazil - Southeast": 1520,
    "Brazil - Midwest": 1650,
    "Brazil - Northeast": 1780,
    "Brazil - North": 1700,
    # Iberian Peninsula
    "Portugal - North (Porto)": 1450,
    "Portugal - Center (Lisbon)": 1600,
    "Portugal - South (Algarve)": 1750,
    "Spain - North": 1400,
    "Spain - Center (Madrid)": 1650,
    "Spain - South (Andalusia)": 1900
}

# Average electricity tariff (2025/2026)
tarifa_media = {
    "Brazil": 0.91,      # R$/kWh
    "Iberian Peninsula": 0.22   # €/kWh (aprox. Portugal/Espanha residencial)
}

# ====================== USER INPUTS ======================
col1, col2 = st.columns(2)

with col1:
    potencia = st.number_input("Installed capacity (kWp)", min_value=1.0, value=5.0, step=0.5)
    regiao = st.selectbox("Installation region", options=list(solar_yield.keys()))

with col2:
    preco_carbono = st.number_input("Carbon credit price (€/tonne)", min_value=10.0, value=50.0, step=5.0)
    if "Brazil" in regiao:
        tarifa_eletrica = st.number_input("Your electricity rate (R$/kWh)", min_value=0.5, value=0.91, step=0.05)
    else:
        tarifa_eletrica = st.number_input("Your electricity rate (€/kWh)", min_value=0.10, value=0.22, step=0.01)
    anos = st.slider("Analysis period (years)", 1, 25, 25)

# ====================== CALCULATIONS ======================region updates
producao_anual_kwh = potencia * solar_yield[regiao]
producao_anual_mwh = producao_anual_kwh / 1000

FATOR_EMISSAO = 0.029  # tCO₂/MWh (aprox. similar na Europa e Brasil)
co2_evitado_anual = producao_anual_mwh * FATOR_EMISSAO

# Convert everything to the base currency (EUR for Iberian, but we handle conversion later)
if "Brazil" in regiao:
    valor_carbono_anual = co2_evitado_anual * (preco_carbono * 5.15)  # convert € to R$ approx
    economia_conta_anual = producao_anual_kwh * tarifa_eletrica
else:
    valor_carbono_anual = co2_evitado_anual * preco_carbono   # already in €
    economia_conta_anual = producao_anual_kwh * tarifa_eletrica

beneficio_total_anual = economia_conta_anual + valor_carbono_anual
valor_total = beneficio_total_anual * anos

# ====================== RESULTS ======================
st.success(f"**Estimated annual production:** {producao_anual_kwh:,.0f} kWh/year")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Electricity bill savings/year", format_currency(economia_conta_anual))
with col_b:
    st.metric("CO₂ avoided/year", f"{co2_evitado_anual:.3f} tonnes")
with col_c:
    st.metric("Carbon credits value/year", format_currency(valor_carbono_anual))

st.metric("**Total annual benefit**", format_currency(beneficio_total_anual))

st.metric(f"**Total benefit over {anos} years**", format_currency(valor_total))

# Chart (simplificado)
df = pd.DataFrame({
    "Year": range(1, anos + 1),
    "Electricity Savings": [economia_conta_anual * y for y in range(1, anos + 1)],
    "Carbon Credits": [valor_carbono_anual * y for y in range(1, anos + 1)],
    "Total Benefit": [beneficio_total_anual * y for y in range(1, anos + 1)]
})

fig = px.line(df, x="Year", y=["Electricity Savings", "Carbon Credits", "Total Benefit"],
              title="Benefit Evolution Over Time", markers=True)
st.plotly_chart(fig, use_container_width=True)

st.info("💡 **Important notes**: Values are estimates. Real savings depend on your location, tariff, roof orientation and shading.")

st.caption("Made for eekwh.net • Now supporting Brazil and the Iberian Peninsula")
