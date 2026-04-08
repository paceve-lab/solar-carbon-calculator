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
    index=0  # Default: USD
)

selected_currency = currency_options[selected_currency_label]
symbol = selected_currency["symbol"]
currency_code = selected_currency["code"]

# Exchange rates (1 unit of selected currency = X BRL) - Updated April 2026
exchange_rates = {
    "USD": 5.15,   # 1 USD ≈ 5.15 BRL
    "EUR": 5.95,   # 1 EUR ≈ 5.95 BRL
    "BRL": 1.0
}

rate_to_brl = exchange_rates[currency_code]

# Function to format any value in the chosen currency
def format_currency(value_brl: float) -> str:
    if value_brl is None or value_brl < 0:
        value_brl = 0.0
    converted = value_brl / rate_to_brl
    return f"{symbol} {converted:,.2f}"

# ====================== OFFICIAL DATA ======================
FATOR_EMISSAO = 0.029  # tCO₂/MWh (MCTI SIN average)
PRECO_CARBONO_PADRAO = 50.0  # R$/tCO₂

# Solar production (kWh/kWp/year) - realistic Brazil averages
regioes = {
    "South": 1350,
    "Southeast": 1520,
    "Midwest": 1650,
    "Northeast": 1780,
    "North": 1700
}

TARIFA_MEDIA_KWH = 0.91  # R$/kWh average

# ====================== PAGE TITLE ======================
st.title("🌞 Solar Carbon & Savings Calculator")
st.markdown("**For homes and small & medium businesses in Brazil** | Updated 2026")

# ====================== USER INPUTS ======================
col1, col2 = st.columns(2)

with col1:
    potencia = st.number_input("Installed capacity (kWp)", min_value=1.0, value=5.0, step=0.5)
    regiao = st.selectbox("Installation region", options=list(regioes.keys()))

with col2:
    preco_carbono = st.number_input("Carbon credit price (R$/tonne)", min_value=10.0, value=PRECO_CARBONO_PADRAO, step=5.0)
    tarifa_eletrica = st.number_input("Your electricity rate (R$/kWh)", min_value=0.5, value=TARIFA_MEDIA_KWH, step=0.05)
    anos = st.slider("Analysis period (years)", 1, 25, 25)

# ====================== CALCULATIONS ======================
producao_anual_kwh = potencia * regioes[regiao]
producao_anual_mwh = producao_anual_kwh / 1000

co2_evitado_anual = producao_anual_mwh * FATOR_EMISSAO
valor_carbono_anual_brl = co2_evitado_anual * preco_carbono
economia_conta_anual_brl = producao_anual_kwh * tarifa_eletrica
beneficio_total_anual_brl = economia_conta_anual_brl + valor_carbono_anual_brl
valor_total_brl = beneficio_total_anual_brl * anos

# ====================== RESULTS ======================
st.success(f"**Estimated annual production:** {producao_anual_kwh:,.0f} kWh/year")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Electricity bill savings/year", format_currency(economia_conta_anual_brl))

with col_b:
    st.metric("CO₂ avoided/year", f"{co2_evitado_anual:.3f} tonnes")

with col_c:
    st.metric("Carbon credits value/year", format_currency(valor_carbono_anual_brl))

st.metric(
    "**Total annual benefit** (savings + credits)", 
    format_currency(beneficio_total_anual_brl),
    delta=f"{format_currency(valor_carbono_anual_brl)} from carbon credits"
)

st.metric(f"**Total benefit over {anos} years**", format_currency(valor_total_brl))

# ====================== CHART ======================
df = pd.DataFrame({
    "Year": range(1, anos + 1),
    "Electricity Savings": [economia_conta_anual_brl * y for y in range(1, anos + 1)],
    "Carbon Credits": [valor_carbono_anual_brl * y for y in range(1, anos + 1)],
    "Total Benefit": [beneficio_total_anual_brl * y for y in range(1, anos + 1)]
})

fig = px.line(df, x="Year", 
              y=["Electricity Savings", "Carbon Credits", "Total Benefit"],
              title="Benefit Evolution Over Time (in selected currency)",
              markers=True)

# Update legend to show currency
fig.update_layout(legend_title="Benefit Type")
st.plotly_chart(fig, use_container_width=True)

# ====================== NOTES ======================
st.caption("Data sources: MCTI emission factor (~0.029 tCO₂/MWh), regional solar yield averages, ANEEL-based electricity tariffs.")

st.info("💡 **Important notes**: \n"
        "• All monetary values are shown in the selected currency using approximate exchange rates.\n"
        "• Electricity savings assume self-consumption with net metering. Real values depend on your distributor and tariff.\n"
        "• Carbon credits for small systems usually require project aggregation and certification. This shows estimated potential only.\n"
        "• This is a simulation tool. Consult a specialist for precise calculations.")

st.divider()
st.markdown("Built for **eekwh.net** – Solar Carbon & Savings Tool")
