import streamlit as st
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title="Dashboard Climático Porto Alegre",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Dashboard Climático - Porto Alegre (Belém Novo)")

# Carrega os dados usando a função cacheada
df = carregar_dados()

st.markdown(f"""
Bem-vindo(a) ao **Dashboard Climático de Porto Alegre - Estação Belém Novo**!

Este aplicativo interativo foi desenvolvido para explorar e visualizar os principais insights sobre as condições meteorológicas registradas na estação meteorológica do INMET localizada em Belém Novo, Porto Alegre/RS.

Através de dados horários detalhados do período de **Maio a Outubro de 2025**, buscamos responder a perguntas como:

* **Como variou a temperatura ao longo dos meses?**
* **Quais foram os períodos de maior precipitação?**
* **Como a umidade relativa se comportou ao longo do tempo?**
* **Qual a relação entre temperatura e pressão atmosférica?**
* **Como foi a distribuição dos ventos?**

---

### 📍 Informações da Estação:
* **Nome:** PORTO ALEGRE - BELEM NOVO
* **Código WMO:** B825
* **Região:** Sul (RS)
* **Latitude:** -30,1861°
* **Longitude:** -51,1783°
* **Altitude:** 3,3 metros
* **Data de Fundação:** 01/05/2025

---

### Como Navegar:
Utilize o menu de navegação na **barra lateral (esquerda)** para explorar as diferentes seções do aplicativo:

* **🌡️ Análise de Temperatura:** Explore variações térmicas, máximas, mínimas e médias
* **💧 Precipitação e Umidade:** Analise os índices de chuva e umidade relativa
* **🌪️ Ventos:** Visualize direção, velocidade e rajadas
* **📊 Análise Geral:** Correlações entre diferentes variáveis meteorológicas
* **📈 Tendências Temporais:** Padrões ao longo dos meses
* **🔍 Dados Detalhados:** Explore os dados brutos com filtros interativos

---

### 📊 Dimensões do Dataset:
- **Período analisado:** Maio a Outubro de 2025
- **Total de registros:** `{df.shape[0]}` medições horárias
- **Variáveis monitoradas:** `{df.shape[1]}` parâmetros meteorológicos

---

Agradecemos a sua visita e esperamos que encontre informações valiosas sobre o clima de Porto Alegre!

**Fonte dos dados:** INMET (Instituto Nacional de Meteorologia)
""")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    temp_media = df['temperatura_ar'].mean()
    st.metric(
        "🌡️ Temperatura Média", 
        f"{temp_media:.1f}°C"
    )

with col2:
    precip_total = df['precipitacao'].sum()
    st.metric(
        "💧 Precipitação Total", 
        f"{precip_total:.1f} mm"
    )

with col3:
    umidade_media = df['umidade_relativa'].mean()
    st.metric(
        "💦 Umidade Média", 
        f"{umidade_media:.1f}%"
    )

with col4:
    vento_medio = df['vento_velocidade'].mean()
    st.metric(
        "🌪️ Velocidade Média Vento", 
        f"{vento_medio:.1f} m/s"
    )

st.markdown("---")

st.header("📋 Prévia dos Dados Meteorológicos")
st.dataframe(
    df.head(20),
    use_container_width=True,
    height=400
)

st.sidebar.success("Selecione uma página acima para começar a explorar os dados!")