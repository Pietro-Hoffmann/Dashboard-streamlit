import streamlit as st
import pandas as pd
import numpy as np


@st.cache_data
def carregar_dados():
    """Carrega e processa os dados meteorológicos do INMET"""
    
    # Carrega o arquivo CSV
    df = pd.read_csv(
        './dataset/INMET_S_RS_B825_PORTO ALEGRE - BELEM NOVO_01-05-2025_A_31-10-2025.CSV',
        sep=';',
        skiprows=8,
        decimal=',',
        encoding='latin1'
    )

    # Remove a última coluna que é gerada a mais
    df = df.iloc[:, :-1]

    df.columns = [
        'data', 'hora', 'precipitacao', 'pressao_atm', 'pressao_max', 
        'pressao_min', 'radiacao_global', 'temperatura_ar', 'temp_orvalho',
        'temperatura_max', 'temperatura_min', 'temp_orvalho_max', 
        'temp_orvalho_min', 'umidade_max', 'umidade_min', 'umidade_relativa',
        'vento_direcao', 'vento_rajada', 'vento_velocidade'
    ]

    # --- PROCESSAMENTO E CRIAÇÃO DE NOVAS FEATURES ---

    # Converter 'hora' para formato de tempo (HH:MM)
    # O formato original é '0', '100', '200', ..., '2300'
    df['hora'] = df['hora'].astype(str).str.replace(' UTC', '').str.zfill(4)
    df['hora'] = df['hora'].str.slice(0, 2) + ':' + df['hora'].str.slice(2, 4)

    # Combinar 'data' e 'hora' em uma única coluna de datetime
    df['data_hora'] = pd.to_datetime(df['data'] + ' ' + df['hora'], format='%Y/%m/%d %H:%M')

    # Extrair componentes de data e hora
    df['mes'] = df['data_hora'].dt.month
    df['dia'] = df['data_hora'].dt.day
    df['hora_num'] = df['data_hora'].dt.hour

    # Criar 'mes_nome'
    meses_dict = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    df['mes_nome'] = df['mes'].map(meses_dict)

    # Criar 'periodo_dia'
    condicoes_periodo = [
        (df['hora_num'] >= 6) & (df['hora_num'] < 12),
        (df['hora_num'] >= 12) & (df['hora_num'] < 18),
        (df['hora_num'] >= 18) & (df['hora_num'] <= 23),
        (df['hora_num'] >= 0) & (df['hora_num'] < 6)
    ]
    periodos = ['Manhã', 'Tarde', 'Noite', 'Madrugada']
    df['periodo_dia'] = np.select(condicoes_periodo, periodos, default='Indefinido')

    # Criar 'intensidade_chuva'
    condicoes_chuva = [
        (df['precipitacao'] == 0),
        (df['precipitacao'] > 0) & (df['precipitacao'] <= 5),
        (df['precipitacao'] > 5) & (df['precipitacao'] <= 25),
        (df['precipitacao'] > 25)
    ]
    intensidades = ['Sem Chuva', 'Chuva Fraca', 'Chuva Moderada', 'Chuva Forte']
    df['intensidade_chuva'] = np.select(condicoes_chuva, intensidades, default='Indefinido')

    # Criar 'classificacao_temp'
    condicoes_temp = [
        (df['temperatura_ar'] < 15),
        (df['temperatura_ar'] >= 15) & (df['temperatura_ar'] < 20),
        (df['temperatura_ar'] >= 20) & (df['temperatura_ar'] < 25),
        (df['temperatura_ar'] >= 25) & (df['temperatura_ar'] < 30),
        (df['temperatura_ar'] >= 30)
    ]
    classificacoes = ['Frio', 'Ameno', 'Agradável', 'Quente', 'Muito Quente']
    df['classificacao_temp'] = np.select(condicoes_temp, classificacoes, default='Indefinido')
    
    # Converter a coluna 'data' para o tipo datetime, se ainda não for
    df['data'] = pd.to_datetime(df['data'], format='%Y/%m/%d')
    
    return df