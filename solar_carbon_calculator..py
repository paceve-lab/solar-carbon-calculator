import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Carbon & Savings Calculator", layout="wide")

# ====================== CURRENCY ======================
st.sidebar.header("🌍 Currency Selection")

currency = st.sidebar.selectbox(
    "Display currency",
    options=["EUR - Euro", "USD - US Dollar", "BRL - Brazilian Real"],
    index=0
)

if currency == "EUR - Euro":
    symbol = "€"
    currency_code = "EUR"
elif currency == "USD - US Dollar":
    symbol = "$"
    currency_code = "USD"
else:
    symbol = "R$"
    currency_code = "BRL"

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
    else:
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

# ====================== CALCULATIONS (sempre em base currency) ======================
producao_anual_kwh = potencia * regioes[regiao]
co2_evitado = (producao_anual_kwh / 1000) * 0.029

if is_brazil:
    # Cálculos em BRL
    economia = producao_anual_kwh * tarifa_eletrica
    carbono = co2_evitado * preco_carbono * 5.15
    custo_sistema = potencia * 3200
else:
    # Cálculos em EUR
    economia = producao_anual_kwh * tarifa_eletrica
    carbono = co2_evitado * preco_carbono
    custo_sistema = potencia * 850

beneficio_anual = economia + carbono
beneficio_total = beneficio_anual * anos
payback = custo_sistema / beneficio_anual if beneficio_anual > 0 else 0

# ====================== CONVERSÃO CORRETA ======================
def format_value(value):
    if currency_code == "BRL":
        return f"R$ {value:,.2f}"
    elif currency_code == "EUR":
        return f"€ {value:,.2f}"
    else:  # USD
        if is_brazil:
            converted = value / 5.15
        else:
            converted = value
        return f"$ {converted:,.2f}"

# ====================== RESULTS ======================
st.success(f"**Annual Production:** {producao_anual_kwh:,.0f} kWh/year")

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric("Electricity Savings / year", format_value(economia))
with col_b:
    st.metric("Carbon Credits / year", format_value(carbono))
with col_c:
    st.metric("Total Annual Benefit", format_value(beneficio_anual))
with col_d:
    st.metric("Estimated System Cost", format_value(custo_sistema))

st.metric(f"**Payback Period**", f"{payback:.1f} years")
st.metric(f"**Total Benefit over {anos} years**", format_value(beneficio_total))

# Charts
tab1, tab2 = st.tabs(["Benefit Evolution", "Monthly Production"])

with tab1:
    df = pd.DataFrame({
        "Year": range(1, anos + 1),
        "Electricity Savings": [economia * y for y in range(1, anos + 1)],
        "Carbon Credits": [carbono * y for y in range(1, anos + 1)],
        "Total Benefit": [beneficio_anual * y for y in range(1, anos + 1)]
    })
    fig = px.line(df, x="Year", y=["Electricity Savings", "Carbon Credits", "Total Benefit"],
                  title="Benefit Evolution Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fator = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11, 0.10, 0.09, 0.08, 0.06, 0.05]
    df_mensal = pd.DataFrame({"Month": meses, "kWh": [producao_anual_kwh * f for f in fator]})
    fig2 = px.bar(df_mensal, x="Month", y="kWh", title="Approximate Monthly Production")
    st.plotly_chart(fig2, use_container_width=True)

st.info("**Note**: Values shown in selected currency using approximate exchange rates (1 USD ≈ 5.15 BRL).")
st.caption("Made for eekwh.net • Brazil & Iberian Peninsula")
