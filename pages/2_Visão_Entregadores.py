# =========================================
# IMPORTANDO BIBLIOTECAS NECESSÁRIAS
# =========================================
from haversine import haversine
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

# ==========================================================================================================================
# CONFIGURAÇÕES INCIAIS
# ==========================================================================================================================
# Definindo o layout da página como wide, para ocupar a tela inteira  
st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

# Definindo o título da página a ser exibido
st.title('Marketplace - Visão Entregadores')

# ==========================================================================================================================
# FUNÇÕES
# ==========================================================================================================================
def global_metrics(col, operator):
    """ Esta função tem como responsabilidade calcular e exibir cada uma das 4 métricas globais do conjunto de dados, um de cada vez. 

        Input:  1. Coluna de interesse - podendo ser 'Delivery_person_Age' ou 'Vehicle_condition';
                2. Operação de interesse - podendo ser 'min' ou 'max'.
        Output: Um único número representando uma métrica global do conjunto de dados.
    """
    if operator == 'max':    
        resultado = df1.loc[:, col].max()
    elif operator == 'min':
        resultado = df1.loc[:, col].min()
    else:
        raise ValueError("Invalid function parameter!")
    return resultado

def toggle_city(df1):
    """ Esta função tem como responsabilidade, alternar entre as cidades únicas em uma coluna de um Dataframe, gerando duas colunas no streamlit para exibição dos dois Dataframes gerados na função 'top_stats()' . 

        Input:  ;
        Output: Duas colunas no streamlit, exibindo dois Dataframes.
    """
    cities = df1.loc[:, 'City'].unique()
    for city in cities:
        st.subheader(city)                       

        df4, df5 = top_stats(df1, city)
                        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### TOP 10 rápidos')
            st.dataframe(df4)
                                                    
        with col2:
            st.markdown('###### TOP 10 lentos')
            st.dataframe(df5)  

def top_stats(df1, city):
    """ Esta função tem como responsabilidade agrupar o Dataframe original, filtrar e devolver dois novos Dataframes. O primeiro contendo os IDs dos 10 entregadores mais rápidos e o segundo, os 10 mais lentos, e os respectivos tempos de entrega para uma cidade específica do conjunto de dados. 

        Input:  Dataframe e Cidade;
        Output: Dois Dataframes.
    """
    cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
                    
    df2 = df1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).mean().sort_values('Time_taken(min)').reset_index()
                    
    filtro = df2.loc[:, 'City'] == city
    df3 = df2.loc[filtro, ['Delivery_person_ID', 'Time_taken(min)'] ]
        
    df3.columns = ['ID do Entregador', 'Duração da Entrega (min)']
                    
    df4 = df3.iloc[: 10, :].reset_index(drop= True)
    df5 = df3.iloc[-10: , :].sort_values('Duração da Entrega (min)', ascending = False).reset_index(drop= True)
        
    return (df4, df5)

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção os dados NaN;
        2. Mudança nos tipos de dados das colunas;
        3. Remoção dos espaços presentes nos dados strings (typos);
        4. Formatação da coluna de datas;
        5. Limpeza da coluna de tempo ( remoção do texto '(min)' da variável numérica.

        Input:  Dataframe
        Output: Dataframe
    """
    # Retirando os espaços indesejados (typos) do conjunto de dados
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Delivery_person_Age'] = df1.loc[:, 'Delivery_person_Age'].str.strip()
    df1.loc[:, 'Delivery_person_Ratings'] = df1.loc[:, 'Delivery_person_Ratings'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    # Descartando (dropando) todas as linhas que contenham 'NaN'
    for i in df1.columns:
      linhas_excl = df1.loc[:, i] == 'NaN'
      df1 = df1.loc[~linhas_excl, :]
    
    # Convertendo a coluna 'Delivery_person_Age' para o tipo int
    df1.loc[:, 'Delivery_person_Age'] = df1.loc[:, 'Delivery_person_Age'].astype(int)
    
    # Convertendo a coluna 'Delivery_person_Ratings' para o tipo float
    df1.loc[:, 'Delivery_person_Ratings'] = df1.loc[:, 'Delivery_person_Ratings'].astype(float)
    
    # Convertendo a coluna 'Order_Date' para o tipo datetime
    df1['Order_Date'] = pd.to_datetime(df1.loc[:, 'Order_Date'],dayfirst=True, format = '%d-%m-%Y')
    
    # Limpando a coluna "Time_taken (min)" e transformando_a em coluna de inteiros
    df1['Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.strip(to_strip = '(min) ')
    df1['Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].astype(int)

    return df1

# =========================================
# RESPONDENDO AS QUESTÕES - VISÃO ENTREGADORES
# =========================================

# =========================================
# BARRA LATERAL NO STREAMLIT
# =========================================
# Configuração e Upload de uma imagem na parte superior da barra lateral 
image_path = ('images/logo.jpg')
image = Image.open( image_path)
st.sidebar.image( image, width = 240)

# Textos a serem exibidos na barra lateral
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Período a ser analisado:')

# Definindo primeiro filtro a ser aplicado na barra lateral, na forma de um controle deslizante
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime( 2022, 4, 6),
    min_value = datetime( 2022, 2, 11),
    max_value = datetime( 2022, 4, 6),
    format = 'DD-MM-YYYY',
    label_visibility='hidden')

st.sidebar.markdown("""---""")

# Definindo segundo filtro a ser aplicado na barra lateral, na forma de uma lista suspensa
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'],)

# Definindo segundo filtro a ser aplicado na barra lateral, na forma de uma lista suspensa
climate_options = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])
    
st.sidebar.markdown("""---""")
# Uma espécie de "crédito" ao autor da página
st.sidebar.markdown('### Powered by linkedin.com/in/maltape/')

# ==========================================================================================================================
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# ==========================================================================================================================

# Importando o dataset
df = pd.read_csv('dataset/train.csv')

# Limpando os dados
df1 = clean_code(df)

# ================================================
# INTEGRANDO OS FILTROS DO STREAMLIT COM OS DADOS
# ================================================

# Aplicando o filtro de data no Dataframe
filtro_data = df1['Order_Date'] <= date_slider

# Aplicando o filtro de condição de tráfego no Dataframe
filtro_trafeg = df1['Road_traffic_density'].isin(traffic_options) 

# Aplicando o filtro de condição de clima  no Dataframe
filtro_clima = df1['Weatherconditions'].isin(climate_options) 

# Filtrando o Dataframe
df1 = df1.loc[filtro_data & filtro_trafeg & filtro_clima , :]

# =========================================
# LAYOUT NO STREAMLIT
# =========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    
    with st.container():
        st.header('Métricas Globais')
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            maior_idade = global_metrics('Delivery_person_Age', 'max')
            col1.metric('Maior idade:', maior_idade)
            
        with col2:
            menor_idade = global_metrics('Delivery_person_Age', 'min')
            col2.metric('Menor idade:', menor_idade)
            
        with col3:
            melhor_cond = global_metrics('Vehicle_condition', 'max')
            col3.metric('Melhor condição de veículo', melhor_cond)
            
        with col4:
            pior_cond = global_metrics('Vehicle_condition', 'min')
            col4.metric('Pior condição de veículo', pior_cond)      
           
        st.markdown("""---""")
    
    with st.container():
        st.header('Avaliações dos Entregadores')
        col1, col2 = st.columns(2)
        with col1:
            
            # definindo colunas a serem filtradas
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            
            # filtragem das linhas
            df2 = df1.loc[:, cols].groupby('Delivery_person_ID').mean().reset_index()
            df2.rename(columns = {'Delivery_person_ID' : 'ID do Entregador', 'Delivery_person_Ratings' : 'Média das Avaliações'}, inplace = True)

            st.dataframe(df2)
            
        with col2:
            with st.container():
                
                cols = ['Delivery_person_Ratings', 'Road_traffic_density']
                df2 = df1.loc[:, cols].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()

                df2.columns = ['Densidade do tráfego', 'Média das Avaliações', 'Desvio Padrão das Avaliações']

                st.dataframe(df2)
                
            with st.container():
               
                cols = ['Delivery_person_Ratings', 'Weatherconditions']
                df2 = df1.loc[:, cols].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()

                df2.columns = ['Condições Climáticas', 'Média das Avaliações', 'Desvio Padrão das Avaliações']

                st.dataframe(df2)
        
        st.markdown("""---""")

    with st.container():
        st.header('Velocidade das entregas')
        with st.container():
            toggle_city(df1)
            
    st.markdown("""---""")