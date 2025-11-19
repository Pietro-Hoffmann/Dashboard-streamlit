import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title='Análise de Temperatura',
    page_icon='🌡️',
    layout='wide'
)

st.title('🌡️ Análise de Temperatura')

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

periodo_dia = st.sidebar.multiselect(
    'Período do dia',
    options=df['periodo_dia'].unique(),
    default=df['periodo_dia'].unique()
)

# Aplica filtros
df_filtrado = df[
    (df['mes'].isin(meses_selecionados)) &
    (df['periodo_dia'].isin(periodo_dia))
].copy()

# Adiciona a classificação de temperatura
def classificar_temperatura(temp):
    if temp < 10:
        return 'Muito Frio'
    elif 10 <= temp < 15:
        return 'Frio'
    elif 15 <= temp < 20:
        return 'Ameno'
    elif 20 <= temp < 25:
        return 'Agradável'
    elif 25 <= temp < 30:
        return 'Quente'
    elif 30 <= temp < 35:
        return 'Muito Quente'
    else:
        return 'Extremamente Quente'

if not df_filtrado.empty:
    df_filtrado['classificacao_temp'] = df_filtrado['temperatura_ar'].apply(classificar_temperatura)

# --- MÉTRICAS PRINCIPAIS ---
st.subheader('📊 Métricas de Temperatura')
col1, col2, col3, col4 = st.columns(4)

# Calcula as métricas apenas se o dataframe não estiver vazio
temp_media = df_filtrado['temperatura_ar'].mean() if not df_filtrado.empty else 0
temp_maxima = df_filtrado['temperatura_max'].max() if not df_filtrado.empty else 0
temp_minima = df_filtrado['temperatura_min'].min() if not df_filtrado.empty else 0
amplitude = temp_maxima - temp_minima if not df_filtrado.empty else 0

with col1:
    st.metric('🌡️ Temperatura Média', f'{temp_media:.1f}°C')

with col2:
    st.metric('🔥 Temperatura Máxima', f'{temp_maxima:.1f}°C')

with col3:
    st.metric('❄️ Temperatura Mínima', f'{temp_minima:.1f}°C')

with col4:
    st.metric('📏 Amplitude Térmica', f'{amplitude:.1f}°C')

st.markdown('---')

# --- GRÁFICO 1: Série Temporal de Temperatura ---
st.subheader('📈 Evolução da Temperatura ao Longo do Tempo')

fig_temp_temporal = go.Figure()

if not df_filtrado.empty:
    fig_temp_temporal.add_trace(go.Scatter(
        x=df_filtrado['data_hora'],
        y=df_filtrado['temperatura_ar'],
        name='Temperatura Atual',
        line=dict(color='#FF6B6B', width=2),
        mode='lines'
    ))

    fig_temp_temporal.add_trace(go.Scatter(
        x=df_filtrado['data_hora'],
        y=df_filtrado['temperatura_max'],
        name='Temperatura Máxima',
        line=dict(color='#FF0000', width=1, dash='dot'),
        mode='lines'
    ))

    fig_temp_temporal.add_trace(go.Scatter(
        x=df_filtrado['data_hora'],
        y=df_filtrado['temperatura_min'],
        name='Temperatura Mínima',
        line=dict(color='#4ECDC4', width=1, dash='dot'),
        mode='lines'
    ))

fig_temp_temporal.update_layout(
    title='Variação de Temperatura (Atual, Máxima e Mínima)',
    xaxis_title='Data e Hora',
    yaxis_title='Temperatura (°C)',
    hovermode='x unified',
    height=500
)

st.plotly_chart(fig_temp_temporal, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 2: Box Plot por Mês ---
st.subheader('📦 Distribuição de Temperatura por Mês')

if not df_filtrado.empty:
    df_filtrado['mes_nome'] = df_filtrado['mes'].map(meses_dict)

    fig_box = px.box(
        df_filtrado,
        x='mes_nome',
        y='temperatura_ar',
        color='mes_nome',
        title='Distribuição de Temperatura por Mês',
        labels={'temperatura_ar': 'Temperatura (°C)', 'mes_nome': 'Mês'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_box.update_layout(
        showlegend=False,
        height=500,
        xaxis_title='Mês',
        yaxis_title='Temperatura (°C)'
    )

    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.warning("Não há dados para exibir o box plot com os filtros selecionados.")


st.markdown('---')

# --- GRÁFICO 3: Temperatura por Período do Dia ---
col1, col2 = st.columns(2)

with col1:
    st.subheader('🕐 Temperatura por Período do Dia')
    
    if not df_filtrado.empty:
        df_periodo = df_filtrado.groupby('periodo_dia')['temperatura_ar'].mean().reset_index()
        df_periodo = df_periodo.sort_values('temperatura_ar', ascending=False)
        
        fig_periodo = px.bar(
            df_periodo,
            x='periodo_dia',
            y='temperatura_ar',
            color='temperatura_ar',
            title='Temperatura Média por Período do Dia',
            labels={'temperatura_ar': 'Temperatura (°C)', 'periodo_dia': 'Período'},
            color_continuous_scale='RdBu_r',
            text='temperatura_ar'
        )
        
        fig_periodo.update_traces(texttemplate='%{text:.1f}°C', textposition='outside')
        fig_periodo.update_layout(height=400)
        
        st.plotly_chart(fig_periodo, use_container_width=True)
    else:
        st.warning("Não há dados para exibir a temperatura por período com os filtros selecionados.")

with col2:
    st.subheader('🎨 Distribuição por Classificação')
    
    fig_donut_class_temp = None
    if not df_filtrado.empty and 'classificacao_temp' in df_filtrado.columns:
        df_class = df_filtrado['classificacao_temp'].value_counts().reset_index()
        df_class.columns = ['classificacao_temp', 'count']
        
        ordem_temp = ['Muito Frio', 'Frio', 'Ameno', 'Agradável', 'Quente', 'Muito Quente', 'Extremamente Quente']
        
        fig_donut_class_temp = px.pie(
            df_class,
            names='classificacao_temp',
            values='count',
            hole=0.4,
            title='Distribuição da Classificação de Temperatura',
            category_orders={'classificacao_temp': ordem_temp},
            color='classificacao_temp',
            color_discrete_map={
                'Muito Frio': '#2166ac',
                'Frio': '#67a9cf',
                'Ameno': '#d1e5f0',
                'Agradável': '#f7f7f7',
                'Quente': '#fddbc7',
                'Muito Quente': '#ef8a62',
                'Extremamente Quente': '#b2182b'
            }
        )
        fig_donut_class_temp.update_traces(textinfo='percent+label')

    if fig_donut_class_temp:
        st.plotly_chart(fig_donut_class_temp, use_container_width=True)
    else:
        st.warning("Não há dados para exibir o gráfico de classificação.")

st.markdown('---')

# --- GRÁFICO 4: Heatmap de Temperatura por Hora e Dia ---
st.subheader('🔥 Mapa de Calor: Temperatura por Hora do Dia')

if not df_filtrado.empty and 'dia' in df_filtrado.columns:
    df_heatmap = df_filtrado.pivot_table(
        values='temperatura_ar',
        index='hora_num',
        columns='dia',
        aggfunc='mean'
    )

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=df_heatmap.values,
        x=df_heatmap.columns,
        y=df_heatmap.index,
        colorscale='RdBu_r',
        text=df_heatmap.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 8},
        colorbar=dict(title="Temp (°C)")
    ))

    fig_heatmap.update_layout(
        title='Temperatura Média por Hora e Dia do Mês',
        xaxis_title='Dia do Mês',
        yaxis_title='Hora do Dia',
        height=600
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.error("A coluna 'dia' não foi encontrada. Isso geralmente é um problema de cache.")
    st.warning("Por favor, limpe o cache do Streamlit no menu (☰) no canto superior direito e recarregue a página.")
    st.write("Colunas disponíveis:", df_filtrado.columns.tolist())

# --- ANÁLISE ESTATÍSTICA ---
st.markdown('---')
st.subheader('📊 Estatísticas Detalhadas')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('**Temperatura do Ar**')
    st.write(df_filtrado['temperatura_ar'].describe())

with col2:
    st.markdown('**Temperatura Máxima**')
    st.write(df_filtrado['temperatura_max'].describe())

with col3:
    st.markdown('**Temperatura Mínima**')
    st.write(df_filtrado['temperatura_min'].describe())