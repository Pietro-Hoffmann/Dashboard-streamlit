import streamlit as st
import plotly.express as px
import pandas as pd
from utils.carrega_dados import carregar_dados

st.set_page_config(
    page_title='Dados Detalhados',
    page_icon='🔍',
    layout='wide'
)

st.title('🔍 Exploração Detalhada dos Dados')

st.markdown("""
Esta página permite explorar os dados brutos com filtros avançados e opções de download.
Use os filtros na barra lateral para personalizar sua análise.
""")

# Carrega os dados
df = carregar_dados()

# --- FILTROS AVANÇADOS ---
st.sidebar.header('🔧 Filtros Avançados')

# Filtro de data
col_data1, col_data2 = st.sidebar.columns(2)
data_inicio = col_data1.date_input(
    'Data Início',
    value=df['data'].min(),
    min_value=df['data'].min(),
    max_value=df['data'].max()
)
data_fim = col_data2.date_input(
    'Data Fim',
    value=df['data'].max(),
    min_value=df['data'].min(),
    max_value=df['data'].max()
)

# Filtro de hora
hora_inicio, hora_fim = st.sidebar.slider(
    'Intervalo de Horas',
    min_value=0,
    max_value=23,
    value=(0, 23)
)

# Filtros de mês
meses_dict = {5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro'}
meses_selecionados = st.sidebar.multiselect(
    'Meses',
    options=sorted(df['mes'].unique()),
    format_func=lambda x: meses_dict.get(x, x),
    default=sorted(df['mes'].unique())
)

# Filtro de período do dia
periodos = st.sidebar.multiselect(
    'Período do Dia',
    options=df['periodo_dia'].unique(),
    default=df['periodo_dia'].unique()
)

# Filtros de temperatura
temp_min, temp_max = st.sidebar.slider(
    'Faixa de Temperatura (°C)',
    min_value=float(df['temperatura_ar'].min()),
    max_value=float(df['temperatura_ar'].max()),
    value=(float(df['temperatura_ar'].min()), float(df['temperatura_ar'].max()))
)

# Filtro de precipitação
apenas_com_chuva = st.sidebar.checkbox('Apenas dias com chuva')

# Aplicar filtros
df_filtrado = df[
    (df['data'] >= pd.to_datetime(data_inicio)) &
    (df['data'] <= pd.to_datetime(data_fim)) &
    (df['hora_num'] >= hora_inicio) &
    (df['hora_num'] <= hora_fim) &
    (df['mes'].isin(meses_selecionados)) &
    (df['periodo_dia'].isin(periodos)) &
    (df['temperatura_ar'] >= temp_min) &
    (df['temperatura_ar'] <= temp_max)
].copy()

if apenas_com_chuva:
    df_filtrado = df_filtrado[df_filtrado['precipitacao'] > 0]

st.sidebar.markdown(f'**{len(df_filtrado)}** registros filtrados')

# --- RESUMO ESTATÍSTICO ---
st.subheader('📊 Resumo Estatístico dos Dados Filtrados')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric('🌡️ Temp. Média', f"{df_filtrado['temperatura_ar'].mean():.1f}°C")

with col2:
    st.metric('💧 Precip. Total', f"{df_filtrado['precipitacao'].sum():.1f} mm")

with col3:
    st.metric('💦 Umidade Média', f"{df_filtrado['umidade_relativa'].mean():.1f}%")

with col4:
    st.metric('🌪️ Vento Médio', f"{df_filtrado['vento_velocidade'].mean():.1f} m/s")

with col5:
    st.metric('⏱️ Pressão Média', f"{df_filtrado['pressao_atm'].mean():.1f} mB")

st.markdown('---')

# --- SELEÇÃO DE COLUNAS PARA VISUALIZAÇÃO ---
st.subheader('🗂️ Personalizar Colunas Exibidas')

todas_colunas = [
    'data', 'hora', 'temperatura_ar', 'temperatura_max', 'temperatura_min',
    'precipitacao', 'umidade_relativa', 'umidade_max', 'umidade_min',
    'pressao_atm', 'vento_velocidade', 'vento_rajada', 'vento_direcao',
    'radiacao_global', 'temp_orvalho', 'classificacao_temp', 
    'intensidade_chuva', 'periodo_dia'
]

colunas_selecionadas = st.multiselect(
    'Selecione as colunas que deseja visualizar:',
    options=todas_colunas,
    default=['data', 'hora', 'temperatura_ar', 'precipitacao', 'umidade_relativa', 
             'vento_velocidade', 'pressao_atm']
)

# --- TABELA DE DADOS ---
st.subheader('📋 Tabela de Dados')

if colunas_selecionadas:
    df_display = df_filtrado[colunas_selecionadas].copy()
    
    # Formatar colunas numéricas
    for col in df_display.columns:
        if df_display[col].dtype in ['float64', 'int64'] and col not in ['data', 'hora']:
            df_display[col] = df_display[col].round(2)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400
    )
    
    # Opção de download
    st.download_button(
        label='📥 Baixar dados filtrados (CSV)',
        data=df_display.to_csv(index=False).encode('utf-8'),
        file_name=f'dados_meteorologicos_filtrados_{data_inicio}_{data_fim}.csv',
        mime='text/csv'
    )
else:
    st.warning('⚠️ Selecione pelo menos uma coluna para visualizar.')

st.markdown('---')

# --- GRÁFICOS PERSONALIZADOS ---
st.subheader('📊 Visualizações Personalizadas')

tab1, tab2, tab3 = st.tabs(['📈 Série Temporal', '📊 Comparação', '🎯 Análise Pontual'])

with tab1:
    st.markdown('**Visualize a evolução temporal de uma variável**')
    
    variavel_tempo = st.selectbox(
        'Selecione a variável:',
        options=['temperatura_ar', 'precipitacao', 'umidade_relativa', 
                'vento_velocidade', 'pressao_atm', 'radiacao_global'],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    fig_tempo = px.line(
        df_filtrado,
        x='data_hora',
        y=variavel_tempo,
        title=f'Evolução de {variavel_tempo.replace("_", " ").title()}',
        labels={variavel_tempo: variavel_tempo.replace('_', ' ').title()}
    )
    
    fig_tempo.update_layout(height=500)
    st.plotly_chart(fig_tempo, use_container_width=True)

with tab2:
    st.markdown('**Compare duas variáveis**')
    
    col1, col2 = st.columns(2)
    
    with col1:
        var1 = st.selectbox(
            'Variável 1:',
            options=['temperatura_ar', 'precipitacao', 'umidade_relativa', 
                    'vento_velocidade', 'pressao_atm'],
            format_func=lambda x: x.replace('_', ' ').title(),
            key='var1'
        )
    
    with col2:
        var2 = st.selectbox(
            'Variável 2:',
            options=['temperatura_ar', 'precipitacao', 'umidade_relativa', 
                    'vento_velocidade', 'pressao_atm'],
            format_func=lambda x: x.replace('_', ' ').title(),
            index=1,
            key='var2'
        )
    
    fig_comp = px.scatter(
        df_filtrado,
        x=var1,
        y=var2,
        color='mes_nome',
        title=f'{var1.replace("_", " ").title()} vs {var2.replace("_", " ").title()}',
        labels={var1: var1.replace('_', ' ').title(), 
                var2: var2.replace('_', ' ').title()},
        trendline='ols'
    )
    
    fig_comp.update_layout(height=500)
    st.plotly_chart(fig_comp, use_container_width=True)

with tab3:
    st.markdown('**Análise por agrupamento**')
    
    col1, col2 = st.columns(2)
    
    with col1:
        variavel_analise = st.selectbox(
            'Variável a analisar:',
            options=['temperatura_ar', 'precipitacao', 'umidade_relativa', 
                    'vento_velocidade', 'pressao_atm'],
            format_func=lambda x: x.replace('_', ' ').title(),
            key='var_analise'
        )
    
    with col2:
        agrupamento = st.selectbox(
            'Agrupar por:',
            options=['mes_nome', 'periodo_dia', 'dia_semana', 'classificacao_temp'],
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    df_agrupado = df_filtrado.groupby(agrupamento)[variavel_analise].agg(['mean', 'min', 'max', 'std']).reset_index()
    
    fig_grupo = px.bar(
        df_agrupado,
        x=agrupamento,
        y='mean',
        error_y='std',
        title=f'{variavel_analise.replace("_", " ").title()} Médio por {agrupamento.replace("_", " ").title()}',
        labels={'mean': f'{variavel_analise.replace("_", " ").title()} Médio'},
        color='mean',
        color_continuous_scale='Viridis'
    )
    
    fig_grupo.update_layout(height=500)
    st.plotly_chart(fig_grupo, use_container_width=True)

st.markdown('---')

# --- ESTATÍSTICAS DESCRITIVAS DETALHADAS ---
st.subheader('📈 Estatísticas Descritivas Completas')

with st.expander('Ver estatísticas detalhadas'):
    colunas_numericas = df_filtrado.select_dtypes(include=['float64', 'int64']).columns
    st.dataframe(
        df_filtrado[colunas_numericas].describe(),
        use_container_width=True
    )

# --- INFORMAÇÕES DO FILTRO APLICADO ---
st.markdown('---')
st.subheader('ℹ️ Resumo dos Filtros Aplicados')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    **📅 Período:**
    - Início: {data_inicio}
    - Fim: {data_fim}
    - Horas: {hora_inicio}h - {hora_fim}h
    """)

with col2:
    st.markdown(f"""
    **🌡️ Temperatura:**
    - Mín: {temp_min}°C
    - Máx: {temp_max}°C
    """)

with col3:
    st.markdown(f"""
    **📊 Registros:**
    - Total original: {len(df)}
    - Após filtros: {len(df_filtrado)}
    - Filtrado: {100 - (len(df_filtrado)/len(df)*100):.1f}%
    """)