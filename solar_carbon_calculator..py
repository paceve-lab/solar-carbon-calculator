import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Carbon & Savings Calculator", layout="wide")

# ====================== CURRENCY CONFIG ======================
st.sidebar.header("🌍 Currency Selection")

currency_options = {
    "USD - US Dollar": {"symbol": "$", "code": "USD"},
    "EUR - Euro":      {"symbol": "€", "code": "EUR"},
    "BRL - Brazilian Real": {"symbol": "R$", "code": "BRL"}
}

selected_currency_label = st.sidebar.selectbox(
    "Display currency", 
    options=list(currency_options.keys()), 
    index=1  # Default: EUR
)

symbol = currency_options[selected_currency_label]["symbol"]
currency_code = currency_options[selected_currency_label]["code"]

# Exchange rates: how many BRL or EUR per unit
exchange_rates = {
    "USD": 5.15,   # 1 USD = 5.15 BRL
    "EUR": 1.0,    # Base for Europe
    "BRL": 1.0
}

rate_to_base = exchange_rates[currency_code]

def format_currency(value_in_base: float) -> str:
    """value_in_base deve estar em EUR para Europa ou em BRL para Brasil"""
    if value_in_base is None or value_in_base < 0:
        value_in_base = 0.0
    converted = value_in_base / rate_to_base if currency_code != "EUR" and currency_code != "BRL" else value_in_base
    # Para BRL mantemos o valor como está (já calculado em BRL)
    if currency_code == "BRL":
        return f"R$ {value_in_base:,.2f}"
    return f"{symbol} {converted:,.2f}"

# ====================== COUNTRY & REGION ======================
st.title("🌞 Solar Carbon & Savings Calculator")
st.markdown("**Brazil & Iberian Peninsula** | Updated 2026")

col1, col2 = st.columns(2)

with col1:
    pais = st.selectbox("Country / País", ["Brazil", "Portugal", "Spain"], index=1)

    if pais == "Brazil":
        regioes = {"South": 1350, "Southeast": 1520, "Midwest": 1650, "Northeast": 1780, "North": 1700}
        tarifa_default = 0.91
        moeda_tarifa = "R$/kWh"
        is_brazil = True
    elif pais == "Portugal":
        regioes = {"North (Porto)": 1450, "Center (Lisbon)": 1600, "South (Algarve)": 1750}
        tarifa_default = 0.22
        moeda_tarifa = "€/kWh"
        is_brazil = False
    else:  # Spain
        regioes = {"North": 1400, "Center (Madrid)": 1650, "South (Andalusia)": 1900}
        tarifa_default = 0.23
        moeda_tarifa = "€/kWh"
        is_brazil = False

    regiao = st.selectbox("Installation region / Região", list(regioes.keys()))

with col2:
    potencia = st.number_input("System size (kWp)", min_value=1.0, value=5.0, step=0.5)
    tarifa_eletrica = st.number_input(f"Electricity rate ({moeda_tarifa})", 
                                      min_value=0.05, value=tarifa_default, step=0.01)
    preco_carbono = st.number_input("Carbon credit price (€/tonne)", min_value=10.0, value=50.0, step=5.0)
    anos = st.slider("Analysis period (years)", 1, 30, 25)

# ====================== CALCULATIONS ======================
producao_anual_kwh = potencia * regioes[regiao]
producao_anual_mwh = producao_anual_kwh / 1000
co2_evitado_anual = producao_anual_mwh * 0.029

# Cálculos base
if is_brazil:
    # Tudo em BRL
    economia_anual = producao_anual_kwh * tarifa_eletrica
    valor_carbono_anual = co2_evitado_anual * (preco_carbono * 5.15)   # converte € para R$
    custo_sistema = potencia * 3200   # BRL por kWp
else:
    # Tudo em EUR
    economia_anual = producao_anual_kwh * tarifa_eletrica
    valor_carbono_anual = co2_evitado_anual * preco_carbono
    custo_sistema = potencia * 850    # EUR por kWp

beneficio_anual = economia_anual + valor_carbono_anual
beneficio_total = beneficio_anual * anos
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

st.metric(f"**Payback Period**", f"{payback_anos:.1f} years")

st.metric(f"**Total Benefit over {anos} years**", format_currency(beneficio_total))

# ====================== CHARTS ======================
tab1, tab2 = st.tabs(["Benefit Evolution", "Monthly Production"])

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
    meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # Produção mensal aproximada (mais no verão)
    fator_mensal = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.10, 0.09, 0.08, 0.06, 0.05]
    producao_mensal = [producao_anual_kwh * f for f in fator_mensal]
    df_mensal = pd.DataFrame({"Month": meses, "kWh": producao_mensal})
    fig2 = px.bar(df_mensal, x="Month", y="kWh", title="Approximate Monthly Production")
    st.plotly_chart(fig2, use_container_width=True)

st.info("**Note**: Values in selected currency. System cost and payback are estimates (2026 average prices).")
st.caption("Made for eekwh.net • Brazil & Iberian Peninsula")
