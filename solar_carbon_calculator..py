import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Carbon & Savings Calculator", layout="wide")

# ====================== CURRENCY CONFIG ======================
st.sidebar.header("🌍 Currency & Settings")

currency_options = {
    "USD - US Dollar": {"symbol": "$", "code": "USD"},
    "EUR - Euro":      {"symbol": "€", "code": "EUR"},
    "BRL - Brazilian Real": {"symbol": "R$", "code": "BRL"}
}

selected_currency_label = st.sidebar.selectbox(
    "Display currency", options=list(currency_options.keys()), index=1
)

symbol = currency_options[selected_currency_label]["symbol"]
currency_code = currency_options[selected_currency_label]["code"]

exchange_rates = {"USD": 5.15, "EUR": 1.0, "BRL": 1.0}
rate = exchange_rates[currency_code]

def format_currency(value: float) -> str:
    if value is None or value < 0:
        value = 0.0
    converted = value / rate if currency_code != "EUR" else value
    return f"{symbol} {converted:,.2f}"

# ====================== TITLE ======================
st.title("🌞 Solar Carbon & Savings Calculator")
st.markdown("**Brazil & Iberian Peninsula** | Updated 2026")

# ====================== INPUTS ======================
col1, col2 = st.columns([1, 1])

with col1:
    pais = st.selectbox("Country / País", ["Brazil", "Portugal", "Spain"], index=1)
    
    if pais == "Brazil":
        regioes = {"South": 1350, "Southeast": 1520, "Midwest": 1650, "Northeast": 1780, "North": 1700}
        tarifa_default = 0.91
        moeda_tarifa = "R$/kWh"
    elif pais == "Portugal":
        regioes = {"North (Porto)": 1450, "Center (Lisbon)": 1600, "South (Algarve)": 1750}
        tarifa_default = 0.22
        moeda_tarifa = "€/kWh"
    else:  # Spain
        regioes = {"North": 1400, "Center (Madrid)": 1650, "South (Andalusia)": 1900}
        tarifa_default = 0.23
        moeda_tarifa = "€/kWh"

    regiao = st.selectbox("Region / Região", options=list(regioes.keys()))
    potencia = st.number_input("System size (kWp)", min_value=1.0, value=5.0, step=0.5)

with col2:
    tarifa_eletrica = st.number_input(f"Electricity rate ({moeda_tarifa})", 
                                      min_value=0.05, value=tarifa_default, step=0.01)
    preco_carbono = st.number_input("Carbon credit price (€/tonne)", min_value=10.0, value=50.0, step=5.0)
    anos = st.slider("Analysis period (years)", 1, 30, 25)

# ====================== CALCULATIONS ======================
producao_anual_kwh = potencia * regioes[regiao]
producao_anual_mwh = producao_anual_kwh / 1000

co2_evitado_anual = producao_anual_mwh * 0.029

if pais == "Brazil":
    valor_carbono_anual = co2_evitado_anual * (preco_carbono * 5.15)
    economia_anual = producao_anual_kwh * tarifa_eletrica
else:
    valor_carbono_anual = co2_evitado_anual * preco_carbono
    economia_anual = producao_anual_kwh * tarifa_eletrica

beneficio_anual = economia_anual + valor_carbono_anual
beneficio_total = beneficio_anual * anos

# Estimativa de custo do sistema (valores médios 2026)
custo_por_kwp = 850 if pais in ["Portugal", "Spain"] else 3200  # EUR vs BRL
custo_sistema = potencia * custo_por_kwp

# Payback Period
payback_anos = custo_sistema / beneficio_anual if beneficio_anual > 0 else 0

# ====================== RESULTS ======================
st.success(f"**Annual Production:** {producao_anual_kwh:,.0f} kWh/year")

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric("Electricity Savings / year", format_currency(economia_anual))
with col_b:
    st.metric("Carbon Credits / year", format_currency(valor_carbono_anual))
with col_c:
    st.metric("Total Annual Benefit", format_currency(beneficio_anual))
with col_d:
    st.metric("Estimated System Cost", format_currency(custo_sistema))

st.metric(f"**Payback Period**", f"{payback_anos:.1f} years", 
          delta="Time to recover investment")

st.metric(f"**Total Benefit over {anos} years**", format_currency(beneficio_total))

# ====================== CHARTS ======================
tab1, tab2 = st.tabs(["Benefit Evolution", "Monthly Production (approx)"])

with tab1:
    df = pd.DataFrame({
        "Year": range(1, anos + 1),
        "Electricity Savings": [economia_anual * y for y in range(1, anos + 1)],
        "Carbon Credits": [valor_carbono_anual * y for y in range(1, anos + 1)],
        "Total Benefit": [beneficio_anual * y for y in range(1, anos + 1)]
    })
    fig = px.line(df, x="Year", y=["Electricity Savings", "Carbon Credits", "Total Benefit"],
                  title="Benefit Evolution Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Produção mensal aproximada (mais no verão)
    meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    producao_mensal = [producao_anual_kwh * 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.10, 0.09, 0.08, 0.06, 0.05]
    df_mensal = pd.DataFrame({"Month": meses, "Production (kWh)": producao_mensal})
    fig2 = px.bar(df_mensal, x="Month", y="Production (kWh)", title="Approximate Monthly Production")
    st.plotly_chart(fig2, use_container_width=True)

# ====================== NOTES ======================
st.info("""
**Important Notes:**
• All values are estimates. Real results depend on your exact location, tariff, roof orientation and shading.
• System cost is an average estimate (2026 prices). 
• Carbon credits for small systems usually require aggregation and certification.
• Payback period does not include maintenance, degradation or incentives.
""")

st.caption("Made for eekwh.net • Supporting Brazil and the Iberian Peninsula")
