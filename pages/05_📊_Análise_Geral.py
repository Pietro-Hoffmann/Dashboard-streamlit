import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title='Análise Geral',
    page_icon='📊',
    layout='wide'
)

st.title('📊 Análise Geral e Correlações')

# Carrega os dados
df = carregar_dados()

st.markdown("""
Esta página apresenta análises multivariadas, explorando as relações entre diferentes 
variáveis meteorológicas registradas na estação de Porto Alegre.
""")

st.markdown('---')

# --- GRÁFICO 1: Matriz de Correlação ---
st.subheader('🔗 Matriz de Correlação entre Variáveis')

# Selecionar variáveis numéricas principais
variaveis_corr = [
    'temperatura_ar', 'temperatura_max', 'temperatura_min',
    'precipitacao', 'umidade_relativa', 'pressao_atm',
    'vento_velocidade', 'vento_rajada', 'radiacao_global'
]

df_corr = df[variaveis_corr].corr()

fig_corr = go.Figure(data=go.Heatmap(
    z=df_corr.values,
    x=df_corr.columns,
    y=df_corr.columns,
    colorscale='RdBu_r',
    zmid=0,
    text=df_corr.values.round(2),
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="Correlação")
))

fig_corr.update_layout(
    title='Matriz de Correlação entre Variáveis Meteorológicas',
    height=700,
    xaxis={'side': 'bottom'},
    yaxis={'side': 'left'}
)

fig_corr.update_xaxes(tickangle=45)

st.plotly_chart(fig_corr, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 2: Scatter Matrix (selecionável) ---
st.subheader('🔍 Matriz de Dispersão Interativa')

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('**Selecione as variáveis:**')
    var_x = st.selectbox('Eixo X', variaveis_corr, index=0)
    var_y = st.selectbox('Eixo Y', variaveis_corr, index=4)
    var_color = st.selectbox('Cor', ['mes', 'periodo_dia', 'intensidade_chuva'], index=0)

with col2:
    meses_dict = {5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro'}
    df['mes_nome'] = df['mes'].map(meses_dict)
    
    fig_scatter = px.scatter(
        df,
        x=var_x,
        y=var_y,
        color=var_color if var_color != 'mes' else 'mes_nome',
        title=f'Relação entre {var_x} e {var_y}',
        labels={var_x: var_x.replace('_', ' ').title(), 
                var_y: var_y.replace('_', ' ').title()},
        trendline='ols',
        hover_data=['data_hora']
    )
    
    fig_scatter.update_layout(height=500)
    
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 3: Análise Multivariada - Temperatura, Umidade e Precipitação ---
st.subheader('🌡️💧 Análise Combinada: Temperatura, Umidade e Precipitação')

fig_multi = go.Figure()

# Temperatura
fig_multi.add_trace(go.Scatter(
    x=df['data_hora'],
    y=df['temperatura_ar'],
    name='Temperatura (°C)',
    yaxis='y',
    line=dict(color='#FF6B6B', width=2)
))

# Umidade
fig_multi.add_trace(go.Scatter(
    x=df['data_hora'],
    y=df['umidade_relativa'],
    name='Umidade (%)',
    yaxis='y2',
    line=dict(color='#4ECDC4', width=2)
))

# Precipitação (barras)
fig_multi.add_trace(go.Bar(
    x=df['data_hora'],
    y=df['precipitacao'],
    name='Precipitação (mm)',
    yaxis='y3',
    marker_color='#95E1D3',
    opacity=0.6
))

fig_multi.update_layout(
    title='Análise Temporal Combinada',
    xaxis=dict(domain=[0, 1]),
    yaxis=dict(
        title=dict(text="Temperatura (°C)", font=dict(color="#FF6B6B")),
        tickfont=dict(color="#FF6B6B")
    ),
    yaxis2=dict(
        title=dict(text="Umidade (%)", font=dict(color="#4ECDC4")),
        tickfont=dict(color="#4ECDC4"),
        anchor="free",
        overlaying="y",
        side="right",
        position=0.95
    ),
    yaxis3=dict(
        title=dict(text="Precipitação (mm)", font=dict(color="#95E1D3")),
        tickfont=dict(color="#95E1D3"),
        anchor="x",
        overlaying="y",
        side="right"
    ),
    height=600,
    hovermode='x unified'
)

st.plotly_chart(fig_multi, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 4: Pressão Atmosférica e sua Relação com Tempo ---
st.subheader('⏱️ Pressão Atmosférica e Condições Meteorológicas')

col1, col2 = st.columns(2)

with col1:
    # Pressão ao longo do tempo
    fig_pressao = go.Figure()
    
    fig_pressao.add_trace(go.Scatter(
        x=df['data_hora'],
        y=df['pressao_atm'],
        name='Pressão Atmosférica',
        line=dict(color='#F38181', width=2),
        fill='tozeroy',
        opacity=0.7
    ))
    
    fig_pressao.update_layout(
        title='Evolução da Pressão Atmosférica',
        xaxis_title='Data e Hora',
        yaxis_title='Pressão (mB)',
        height=400
    )
    
    st.plotly_chart(fig_pressao, use_container_width=True)

with col2:
    # Relação pressão x precipitação
    fig_pressao_precip = px.scatter(
        df[df['precipitacao'] > 0],
        x='pressao_atm',
        y='precipitacao',
        size='precipitacao',
        color='intensidade_chuva',
        title='Pressão vs Precipitação',
        labels={
            'pressao_atm': 'Pressão (mB)',
            'precipitacao': 'Precipitação (mm)'
        },
        color_discrete_sequence=px.colors.sequential.Blues
    )
    
    fig_pressao_precip.update_layout(height=400)
    
    st.plotly_chart(fig_pressao_precip, use_container_width=True)

st.markdown('---')

# --- GRÁFICO 5: Radiação Solar ---
st.subheader('☀️ Radiação Solar')

df_radiacao = df[df['radiacao_global'] > 0].copy()

fig_radiacao = go.Figure()

fig_radiacao.add_trace(go.Scatter(
    x=df_radiacao['data_hora'],
    y=df_radiacao['radiacao_global'],
    name='Radiação Global',
    line=dict(color='#FFA500', width=2),
    fill='tozeroy'
))

fig_radiacao.update_layout(
    title='Radiação Solar Global ao Longo do Tempo',
    xaxis_title='Data e Hora',
    yaxis_title='Radiação (Kj/m²)',
    height=500
)

st.plotly_chart(fig_radiacao, use_container_width=True)

# --- Radiação por hora do dia ---
st.subheader('☀️ Radiação Solar Média por Hora do Dia')

df_rad_hora = df_radiacao.groupby('hora_num')['radiacao_global'].mean().reset_index()

fig_rad_hora = px.bar(
    df_rad_hora,
    x='hora_num',
    y='radiacao_global',
    title='Radiação Solar Média por Hora',
    labels={'hora_num': 'Hora do Dia', 'radiacao_global': 'Radiação (Kj/m²)'},
    color='radiacao_global',
    color_continuous_scale='YlOrRd'
)

fig_rad_hora.update_layout(height=400)

st.plotly_chart(fig_rad_hora, use_container_width=True)

st.markdown('---')

# --- INSIGHTS ESTATÍSTICOS ---
st.subheader('📈 Principais Insights Estatísticos')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('**🌡️ Temperatura**')
    corr_temp_umid = df['temperatura_ar'].corr(df['umidade_relativa'])
    st.metric('Correlação Temp x Umidade', f'{corr_temp_umid:.3f}')
    st.caption('Negativa indica: quando um sobe, outro desce')

with col2:
    st.markdown('**💧 Precipitação**')
    dias_sem_chuva = ((df.groupby('data')['precipitacao'].sum() == 0).sum() / 
                      df['data'].nunique() * 100)
    st.metric('Dias sem Chuva', f'{dias_sem_chuva:.1f}%')
    st.caption('Percentual de dias sem precipitação')

with col3:
    st.markdown('**🌪️ Vento**')
    corr_vento_pressao = df['vento_velocidade'].corr(df['pressao_atm'])
    st.metric('Correlação Vento x Pressão', f'{corr_vento_pressao:.3f}')
    st.caption('Relação entre velocidade do vento e pressão')

st.markdown('---')

st.info("""
**💡 Como interpretar as correlações:**
- **Valores próximos de +1**: Correlação positiva forte (quando uma variável aumenta, a outra também aumenta)
- **Valores próximos de -1**: Correlação negativa forte (quando uma variável aumenta, a outra diminui)
- **Valores próximos de 0**: Pouca ou nenhuma correlação linear
""")