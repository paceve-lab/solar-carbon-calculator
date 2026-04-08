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
    index=1  # Default: EUR
)

selected_currency = currency_options[selected_currency_label]
symbol = selected_currency["symbol"]
currency_code = selected_currency["code"]

exchange_rates = {"USD": 5.15, "EUR": 1.0, "BRL": 1.0}
rate_to_base = exchange_rates[currency_code]

def format_currency(value_base: float) -> str:
    if value_base is None or value_base < 0:
        value_base = 0.0
    converted = value_base / rate_to_base if currency_code != "EUR" else value_base
    return f"{symbol} {converted:,.2f}"

# ====================== MAIN TITLE ======================
st.title("🌞 Solar Carbon & Savings Calculator")
st.markdown("**For Brazil and the Iberian Peninsula** | Updated 2026")

# ====================== COUNTRY & REGION SELECTION ======================
col1, col2 = st.columns(2)

with col1:
    pais = st.selectbox(
        "Select Country / País",
        options=["Brazil", "Portugal", "Spain"],
        index=1   # Default: Portugal
    )

# Define regions according to selected country
if pais == "Brazil":
    regioes = {
        "South": 1350,
        "Southeast": 1520,
        "Midwest": 1650,
        "Northeast": 1780,
        "North": 1700
    }
    tarifa_default = 0.91
    moeda_tarifa = "R$/kWh"
elif pais == "Portugal":
    regioes = {
        "North (Porto)": 1450,
        "Center (Lisbon)": 1600,
        "South (Algarve)": 1750
    }
    tarifa_default = 0.22
    moeda_tarifa = "€/kWh"
else:  # Spain
    regioes = {
        "North": 1400,
        "Center (Madrid)": 1650,
        "South (Andalusia)": 1900
    }
    tarifa_default = 0.23
    moeda_tarifa = "€/kWh"

with col2:
    regiao = st.selectbox("Installation region / Região", options=list(regioes.keys()))

# ====================== OTHER INPUTS ======================
potencia = st.number_input("Installed capacity (kWp)", min_value=1.0, value=5.0, step=0.5)

col_a, col_b = st.columns(2)
with col_a:
    tarifa_eletrica = st.number_input(f"Your electricity rate ({moeda_tarifa})", 
                                      min_value=0.05, value=tarifa_default, step=0.01)
with col_b:
    anos = st.slider("Analysis period (years)", 1, 25, 25)

preco_carbono = st.number_input("Carbon credit price (€/tonne)", min_value=10.0, value=50.0, step=5.0)

# ====================== CALCULATIONS ======================
producao_anual_kwh = potencia * regioes[regiao]
producao_anual_mwh = producao_anual_kwh / 1000

FATOR_EMISSAO = 0.029
co2_evitado_anual = producao_anual_mwh * FATOR_EMISSAO

if pais == "Brazil":
    valor_carbono_anual = co2_evitado_anual * (preco_carbono * 5.15)   # convert to R$
    economia_conta_anual = producao_anual_kwh * tarifa_eletrica
else:
    valor_carbono_anual = co2_evitado_anual * preco_carbono
    economia_conta_anual = producao_anual_kwh * tarifa_eletrica

beneficio_total_anual = economia_conta_anual + valor_carbono_anual
valor_total = beneficio_total_anual * anos

# ====================== RESULTS ======================
st.success(f"**Estimated annual production:** {producao_anual_kwh:,.0f} kWh/year")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Electricity bill savings/year", format_currency(economia_conta_anual))
with col2:
    st.metric("CO₂ avoided/year", f"{co2_evitado_anual:.3f} tonnes")
with col3:
    st.metric("Carbon credits value/year", format_currency(valor_carbono_anual))

st.metric("**Total annual benefit**", format_currency(beneficio_total_anual))
st.metric(f"**Total benefit over {anos} years**", format_currency(valor_total))

# Chart
df = pd.DataFrame({
    "Year": range(1, anos + 1),
    "Electricity Savings": [economia_conta_anual * y for y in range(1, anos + 1)],
    "Carbon Credits": [valor_carbono_anual * y for y in range(1, anos + 1)],
    "Total Benefit": [beneficio_total_anual * y for y in range(1, anos + 1)]
})

fig = px.line(df, x="Year", y=["Electricity Savings", "Carbon Credits", "Total Benefit"],
              title="Benefit Evolution Over Time", markers=True)
st.plotly_chart(fig, use_container_width=True)

st.info("💡 All monetary values are shown in the selected currency. Results are estimates only.")
st.caption("Made for eekwh.net • Supporting Brazil and the Iberian Peninsula")
