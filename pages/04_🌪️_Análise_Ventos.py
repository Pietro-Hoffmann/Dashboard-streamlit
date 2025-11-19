import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title='Análise de Ventos',
    page_icon='🌪️',
    layout='wide'
)

st.title('🌪️ Análise de Ventos')

# Carrega os dados
df = carregar_dados()

# --- FILTROS ---
st.sidebar.header('🔍 Filtros')
meses_disponiveis = sorted(df['mes'].unique())
meses_dict = {5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro'}
meses_selecionados = st.sidebar.multiselect(
    'Selecione os meses',
    options=meses_disponiveis,
    format_func=lambda x: meses_dict.get(x, x),
    default=meses_disponiveis
)

# Aplica filtros
df_filtrado = df[df['mes'].isin(meses_selecionados)].copy()

# --- MÉTRICAS PRINCIPAIS ---
st.subheader('📊 Métricas de Vento')
col1, col2, col3, col4 = st.columns(4)

with col1:
    vento_medio = df_filtrado['vento_velocidade'].mean()
    st.metric('🌬️ Velocidade Média', f'{vento_medio:.1f} m/s')

with col2:
    vento_max = df_filtrado['vento_velocidade'].max()
    st.metric('💨 Velocidade Máxima', f'{vento_max:.1f} m/s')

with col3:
    rajada_max = df_filtrado['vento_rajada'].max()
    st.metric('🌪️ Rajada Máxima', f'{rajada_max:.1f} m/s')

with col4:
    # Converter m/s para km/h
    vento_kmh = vento_medio * 3.6
    st.metric('🚗 Velocidade Média', f'{vento_kmh:.1f} km/h')

st.markdown('---')

# --- GRÁFICO 1: Velocidade do Vento ao Longo do Tempo ---
st.subheader('📈 Evolução da Velocidade do Vento')

fig_vento_tempo = go.Figure()

fig_vento_tempo.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['vento_velocidade'],
    name='Velocidade do Vento',
    line=dict(color='#00D084', width=2),
    mode='lines'
))

fig_vento_tempo.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['vento_rajada'],
    name='Rajadas de Vento',
    line=dict(color='#FF6B6B', width=1, dash='dot'),
    mode='lines'
))

fig_vento_tempo.update_layout(
    title='Velocidade do Vento e Rajadas ao Longo do Tempo',
    xaxis_title='Data e Hora',
    yaxis_title='Velocidade (m/s)',
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_vento_tempo, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 2: Rosa dos Ventos ---
st.subheader('🧭 Rosa dos Ventos - Direção Predominante')

# Preparar dados para rosa dos ventos
df_direcao = df_filtrado.dropna(subset=['vento_direcao', 'vento_velocidade'])

# Criar faixas de direção (16 pontos cardeais)
def direcao_cardeal(graus):
    if pd.isna(graus):
        return 'N/A'
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    idx = int((graus + 11.25) / 22.5) % 16
    return dirs[idx]

df_direcao['direcao_cardeal'] = df_direcao['vento_direcao'].apply(direcao_cardeal)

# Criar faixas de velocidade
def faixa_velocidade(vel):
    if pd.isna(vel):
        return 'N/A'
    if vel < 2:
        return '0-2 m/s'
    elif vel < 4:
        return '2-4 m/s'
    elif vel < 6:
        return '4-6 m/s'
    elif vel < 8:
        return '6-8 m/s'
    else:
        return '>8 m/s'

df_direcao['faixa_vel'] = df_direcao['vento_velocidade'].apply(faixa_velocidade)

# Agrupar dados
df_rosa = df_direcao.groupby(['direcao_cardeal', 'faixa_vel']).size().reset_index(name='count')

fig_rosa = px.bar_polar(
    df_rosa,
    r='count',
    theta='direcao_cardeal',
    color='faixa_vel',
    title='Rosa dos Ventos - Direção e Intensidade',
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig_rosa.update_layout(height=600)

st.plotly_chart(fig_rosa, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 3: Distribuição de Velocidades ---
col1, col2 = st.columns(2)

with col1:
    st.subheader('📊 Histograma de Velocidades')
    
    fig_hist = px.histogram(
        df_filtrado,
        x='vento_velocidade',
        nbins=30,
        title='Distribuição de Velocidade do Vento',
        labels={'vento_velocidade': 'Velocidade (m/s)'},
        color_discrete_sequence=['#00D084']
    )
    
    fig_hist.update_layout(
        height=400,
        yaxis_title='Frequência'
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader('📈 Box Plot de Velocidades')
    
    df_filtrado['mes_nome'] = df_filtrado['mes'].map(meses_dict)
    
    fig_box = px.box(
        df_filtrado,
        x='mes_nome',
        y='vento_velocidade',
        color='mes_nome',
        title='Distribuição de Velocidade por Mês',
        labels={'vento_velocidade': 'Velocidade (m/s)', 'mes_nome': 'Mês'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_box.update_layout(
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 4: Velocidade por Período do Dia ---
st.subheader('🕐 Velocidade do Vento por Período do Dia')

df_periodo = df_filtrado.groupby('periodo_dia').agg({
    'vento_velocidade': 'mean',
    'vento_rajada': 'mean'
}).reset_index()

fig_periodo = go.Figure()

fig_periodo.add_trace(go.Bar(
    x=df_periodo['periodo_dia'],
    y=df_periodo['vento_velocidade'],
    name='Velocidade Média',
    marker_color='#00D084',
    text=df_periodo['vento_velocidade'].round(2),
    textposition='outside'
))

fig_periodo.add_trace(go.Bar(
    x=df_periodo['periodo_dia'],
    y=df_periodo['vento_rajada'],
    name='Rajada Média',
    marker_color='#FF6B6B',
    text=df_periodo['vento_rajada'].round(2),
    textposition='outside'
))

fig_periodo.update_layout(
    title='Velocidade Média do Vento por Período do Dia',
    xaxis_title='Período do Dia',
    yaxis_title='Velocidade (m/s)',
    barmode='group',
    height=500
)

st.plotly_chart(fig_periodo, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 5: Mapa de Calor - Direção do Vento ---
st.subheader('🔥 Mapa de Calor: Direção do Vento por Hora')

df_heatmap = df_filtrado.pivot_table(
    values='vento_direcao',
    index='hora_num',
    columns='dia',
    aggfunc='mean'
)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=df_heatmap.values,
    x=df_heatmap.columns,
    y=df_heatmap.index,
    colorscale='HSV',
    colorbar=dict(title="Direção (°)")
))

fig_heatmap.update_layout(
    title='Direção do Vento por Hora e Dia (em graus)',
    xaxis_title='Dia do Mês',
    yaxis_title='Hora do Dia',
    height=600
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# --- ANÁLISE ESTATÍSTICA ---
st.markdown('---')
st.subheader('📊 Estatísticas Detalhadas')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('**Velocidade do Vento**')
    st.write(df_filtrado['vento_velocidade'].describe())

with col2:
    st.markdown('**Rajadas de Vento**')
    st.write(df_filtrado['vento_rajada'].describe())

with col3:
    st.markdown('**Direção do Vento**')
    st.write(df_filtrado['vento_direcao'].describe())

# --- ESCALA BEAUFORT ---
st.markdown('---')
st.info("""
**💡 Escala de Beaufort (conversão aproximada):**
- **0-2 m/s** (0-7 km/h): Vento calmo
- **2-4 m/s** (7-14 km/h): Brisa leve
- **4-6 m/s** (14-22 km/h): Brisa moderada
- **6-8 m/s** (22-29 km/h): Brisa forte
- **>8 m/s** (>29 km/h): Vento forte ou superior
""")