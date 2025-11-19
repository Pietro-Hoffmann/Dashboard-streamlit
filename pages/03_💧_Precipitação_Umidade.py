import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title='Precipitação e Umidade',
    page_icon='💧',
    layout='wide'
)

st.title('💧 Análise de Precipitação e Umidade')

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
st.subheader('📊 Métricas Principais')
col1, col2, col3, col4 = st.columns(4)

with col1:
    precip_total = df_filtrado['precipitacao'].sum()
    st.metric('💧 Precipitação Total', f'{precip_total:.1f} mm')

with col2:
    precip_media = df_filtrado['precipitacao'].mean()
    st.metric('📊 Precipitação Média', f'{precip_media:.2f} mm')

with col3:
    umidade_media = df_filtrado['umidade_relativa'].mean()
    st.metric('💦 Umidade Média', f'{umidade_media:.1f}%')

with col4:
    dias_chuva = (df_filtrado.groupby('data')['precipitacao'].sum() > 0).sum()
    st.metric('🌧️ Dias com Chuva', f'{dias_chuva} dias')

st.markdown('---')

# --- GRÁFICO 1: Precipitação Acumulada ao Longo do Tempo ---
st.subheader('📈 Precipitação Acumulada ao Longo do Tempo')

df_filtrado['precip_acumulada'] = df_filtrado['precipitacao'].cumsum()

fig_precip_acum = go.Figure()

fig_precip_acum.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['precip_acumulada'],
    fill='tozeroy',
    name='Precipitação Acumulada',
    line=dict(color='#4A90E2', width=2)
))

fig_precip_acum.update_layout(
    title='Precipitação Acumulada',
    xaxis_title='Data e Hora',
    yaxis_title='Precipitação (mm)',
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_precip_acum, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 2: Precipitação Horária ---
col1, col2 = st.columns(2)

with col1:
    st.subheader('🌧️ Precipitação Horária')
    
    df_precip_hora = df_filtrado[df_filtrado['precipitacao'] > 0].copy()
    
    if not df_precip_hora.empty:
        fig_precip_bars = px.bar(
            df_precip_hora,
            x='data_hora',
            y='precipitacao',
            color='intensidade_chuva',
            title='Eventos de Precipitação',
            labels={'precipitacao': 'Precipitação (mm)', 'data_hora': 'Data e Hora'},
            color_discrete_map={
                'Chuva leve': '#A8DADC',
                'Chuva moderada': '#457B9D',
                'Chuva forte': '#1D3557',
                'Chuva muito forte': '#000814'
            }
        )
        
        fig_precip_bars.update_layout(height=400)
        st.plotly_chart(fig_precip_bars, use_container_width=True)
    else:
        st.info('Não há eventos de precipitação no período selecionado.')

with col2:
    st.subheader('📊 Distribuição por Intensidade')
    
    df_intensidade = df_filtrado['intensidade_chuva'].value_counts().reset_index()
    df_intensidade.columns = ['Intensidade', 'Frequência']
    
    fig_intensidade = px.pie(
        df_intensidade,
        values='Frequência',
        names='Intensidade',
        title='Distribuição de Intensidade de Chuva',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues
    )
    
    fig_intensidade.update_layout(height=400)
    st.plotly_chart(fig_intensidade, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 3: Precipitação por Mês ---
st.subheader('📅 Precipitação Total por Mês')

df_filtrado['mes_nome'] = df_filtrado['mes'].map(meses_dict)
df_precip_mes = df_filtrado.groupby('mes_nome')['precipitacao'].sum().reset_index()

fig_precip_mes = px.bar(
    df_precip_mes,
    x='mes_nome',
    y='precipitacao',
    color='precipitacao',
    title='Precipitação Total por Mês',
    labels={'precipitacao': 'Precipitação (mm)', 'mes_nome': 'Mês'},
    color_continuous_scale='Blues',
    text='precipitacao'
)

fig_precip_mes.update_traces(texttemplate='%{text:.1f} mm', textposition='outside')
fig_precip_mes.update_layout(height=500)

st.plotly_chart(fig_precip_mes, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 4: Análise de Umidade ---
st.subheader('💦 Análise de Umidade Relativa')

fig_umidade = go.Figure()

fig_umidade.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['umidade_relativa'],
    name='Umidade Relativa',
    line=dict(color='#56CCF2', width=2),
    fill='tozeroy',
    opacity=0.7
))

fig_umidade.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['umidade_max'],
    name='Umidade Máxima',
    line=dict(color='#2F80ED', width=1, dash='dot'),
    mode='lines'
))

fig_umidade.add_trace(go.Scatter(
    x=df_filtrado['data_hora'],
    y=df_filtrado['umidade_min'],
    name='Umidade Mínima',
    line=dict(color='#BB6BD9', width=1, dash='dot'),
    mode='lines'
))

fig_umidade.update_layout(
    title='Evolução da Umidade Relativa',
    xaxis_title='Data e Hora',
    yaxis_title='Umidade Relativa (%)',
    height=500,
    hovermode='x unified'
)

st.plotly_chart(fig_umidade, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 5: Correlação Temperatura x Umidade ---
st.subheader('🔄 Correlação entre Temperatura e Umidade')

fig_scatter = px.scatter(
    df_filtrado,
    x='temperatura_ar',
    y='umidade_relativa',
    color='precipitacao',
    size=df_filtrado['precipitacao'].fillna(0),
    title='Relação entre Temperatura e Umidade (tamanho = precipitação)',
    labels={
        'temperatura_ar': 'Temperatura (°C)',
        'umidade_relativa': 'Umidade Relativa (%)',
        'precipitacao': 'Precipitação (mm)'
    },
    color_continuous_scale='Blues',
    hover_data=['data_hora']
)

fig_scatter.update_layout(height=500)

st.plotly_chart(fig_scatter, use_container_width=True)

# --- ANÁLISE ESTATÍSTICA ---
st.markdown('---')
st.subheader('📊 Estatísticas Detalhadas')

col1, col2 = st.columns(2)

with col1:
    st.markdown('**Precipitação**')
    st.write(df_filtrado['precipitacao'].describe())

with col2:
    st.markdown('**Umidade Relativa**')
    st.write(df_filtrado['umidade_relativa'].describe())

# --- INFORMAÇÕES ADICIONAIS ---
st.markdown('---')
st.info("""
**💡 Interpretação dos dados:**
- **Precipitação Total**: Soma de toda a chuva registrada no período
- **Umidade Relativa**: Percentual de vapor d'água no ar em relação ao máximo possível
- **Intensidade de Chuva**: Classificação baseada na quantidade de mm por hora
""")