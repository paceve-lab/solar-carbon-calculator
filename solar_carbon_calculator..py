import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Carbon & Savings Calculator", layout="centered")
st.title("🌞 Solar Energy Calculator: Bill Savings + Carbon Credits")
st.markdown("**For homes, small & medium businesses in Brazil** | Updated 2026")

# ====================== OFFICIAL DATA ======================
FATOR_EMISSAO = 0.029  # tCO₂/MWh (MCTI SIN average ~2025/2026)
PRECO_CARBONO_PADRAO = 50.0  # R$/tCO₂ (voluntary market average)

# Solar production factors (kWh/kWp/year) - realistic Brazil averages
regioes = {
    "South": 1350,
    "Southeast": 1520,
    "Midwest": 1650,
    "Northeast": 1780,
    "North": 1700
}

# Average electricity tariff (residential/small business) - approx. 2025/2026
TARIFA_MEDIA_KWH = 0.91  # R$/kWh (source: ANEEL & market data; varies by distributor)

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
valor_carbono_anual = co2_evitado_anual * preco_carbono

economia_conta_anual = producao_anual_kwh * tarifa_eletrica
beneficio_total_anual = economia_conta_anual + valor_carbono_anual

valor_total = beneficio_total_anual * anos

# ====================== RESULTS ======================
st.success(f"**Estimated annual production:** {producao_anual_kwh:,.0f} kWh/year")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Electricity bill savings/year", f"R$ {economia_conta_anual:,.2f}")
with col_b:
    st.metric("CO₂ avoided/year", f"{co2_evitado_anual:.3f} tonnes")
with col_c:
    st.metric("Carbon credits value/year", f"R$ {valor_carbono_anual:,.2f}")

st.metric("**Total annual benefit** (savings + credits)", f"R$ {beneficio_total_anual:,.2f}", 
          delta=f"R$ {beneficio_total_anual - economia_conta_anual:,.2f} from credits")

st.metric(f"**Total benefit over {anos} years**", f"R$ {valor_total:,.2f}")

# Chart
df = pd.DataFrame({
    "Year": range(1, anos + 1),
    "Electricity Savings (R$)": [economia_conta_anual * y for y in range(1, anos + 1)],
    "Carbon Credits (R$)": [valor_carbono_anual * y for y in range(1, anos + 1)],
    "Total Benefit (R$)": [beneficio_total_anual * y for y in range(1, anos + 1)]
})

fig = px.line(df, x="Year", y=["Electricity Savings (R$)", "Carbon Credits (R$)", "Total Benefit (R$)"],
              title="Benefit Evolution Over Time", markers=True)
st.plotly_chart(fig, use_container_width=True)

st.caption("Data sources: MCTI emission factor (~0.029 tCO₂/MWh), regional solar yield averages, ANEEL-based electricity tariffs (~R$0.91/kWh average).")
st.info("💡 **Important notes**: \n"
        "• Electricity savings assume self-consumption (net metering). Real savings depend on your distributor and tariff. \n"
        "• Carbon credits for small systems (<75 kW) usually require aggregation/certification (Verra, Gold Standard or future Brazilian SBCE). This shows **potential value** only. \n"
        "• Values are estimates – consult a specialist for your specific case.")

st.divider()
st.markdown("Built for **eekwh.net** – Solar Carbon & Savings Tool")
