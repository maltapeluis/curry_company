# ==========================================================================================================================
# IMPORTANDO BIBLIOTECAS NECESSÁRIAS
# ==========================================================================================================================

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
st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

# Definindo o título da página a ser exibido 
st.title('Marketplace - Visão Cliente')

# ==========================================================================================================================
# FUNÇÕES
# ==========================================================================================================================
def order_map(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar um mapa geográfico contendo a localização central dos pedidos por cada cidade e condição de tráfego. A localização central nada mais é do que o ponto médio dos pedidos.
    
        Dados de interesse:
        1. Coluna das Cidades;
        2. Coluna das condições de tráfego;
        3. Coluna das longitudes da localização dos pedidos;
        4. Coluna das latitudes da localização dos pedidos.

        Objetivo do gráfico gerado: Mapear as localizações centrais para cada pedido do conjunto de dados, informando ao clique, a respectiva condição de tráfego e a cidade.

        Input:  Dataframe
        Output: Mapa plotado na tela.
    """
    # definindo colunas a serem filtradas
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    # filtragem das linhas
    df2 = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df2.rename( columns = {'Delivery_location_latitude' : 'Delivery_location_latitude (median)', 'Delivery_location_longitude' : 'Delivery_location_longitude (median)'}, inplace = True)
    # gerando o mapa geográfico das localizações centrais
    map = folium.Map()
    for index, location_info in df2.iterrows():
      folium.Marker([location_info['Delivery_location_latitude (median)'],
                     location_info['Delivery_location_longitude (median)']],
                     popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)
    return

def week_personID_order_share(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar uma imagem contendo os elementos de um gráfico de linha.
    
        Dados de interesse:
        1. Coluna dos IDs das entregas;
        2. Coluna das semanas em que cada pedido ocorreu;
        3. Coluna dos IDs dos entregadores.

        Objetivo do gráfico gerado: Quantificar o número médio de pedidos por cada entregador por semana.

        Input:  Dataframe
        Output: Objeto fig a ser plotado.
    """
    # definindo colunas a serem filtradas
    cols_1 = ['ID','Week_of_year']
    cols_2 = ['Delivery_person_ID','Week_of_year']
    # filtragem das linhas
    df2 = df1.loc[:, cols_1].groupby(['Week_of_year']).count().reset_index()
    df2.rename(columns = {'ID' : 'ID (count)'}, inplace = True)
    df3 = df1.loc[:, cols_2].groupby(['Week_of_year']).nunique().reset_index()
    df3.rename(columns = {'Delivery_person_ID' : 'Delivery_person_ID (nunique)'}, inplace = True)
    # Mesclando os dataframes 'df1' e 'df2' filtrados anteriormente
    df4 = pd.merge(df2, df3, how = 'inner')
    df4['media_por_entreg_unico'] = df4.loc[:, 'ID (count)'] / df4.loc[:, 'Delivery_person_ID (nunique)']
    # gerando o gráfico de linhas e armazenando-o em 'fig'
    fig = (px.line(df4, x = 'Week_of_year', y = 'media_por_entreg_unico', 
                   labels = {'Week_of_year' : '# Semana do ano', 
                             'media_por_entreg_unico' : 'Média de entregas por entregador'}))
    return fig

def order_by_week(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar uma imagem contendo os elementos de um gráfico de linha.
    
        Dados de interesse:
        1. Coluna dos IDs das entregas;
        2. Coluna das semanas em que cada pedido ocorreu.

        Objetivo do gráfico gerado: Quantificar o número de pedidos por semana.

        Input:  Dataframe
        Output: Objeto fig a ser plotado.
    """
    # criando uma coluna de semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime( '%U')
    # definindo colunas a serem filtradas
    cols = ['ID', 'Week_of_year']
    # filtragem das linhas
    df2 = df1.loc[:, cols].groupby('Week_of_year').count().reset_index()
    df2.rename(columns = {'ID' : 'ID (count)'}, inplace = True)
    # gerando o gráfico de linhas e armazenando-o em 'fig'
    fig = (px.line(df2, x = 'Week_of_year', y = 'ID (count)', 
                   labels = {'ID (count)': 'Pedidos registrados', 
                             'Week_of_year' : '# Semana do ano'}))
    return fig

def city_and_traffic_order_share(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar uma imagem contendo os elementos de um gráfico de pontos.
    
        Dados de interesse:
        1. Coluna dos IDs das entregas;
        2. Coluna das condições de trânsito;
        3. Coluna das Cidades.

        Objetivo do gráfico gerado: Quantificar a porcentagem de pedidos realizados por cidade em cada uma das condições de trânsito.

        Input:  Dataframe
        Output: Objeto fig a ser plotado.
    """
    # definindo colunas a serem filtradas
    cols = ['Road_traffic_density', 'City', 'ID']
    # filtragem das linhas
    df2 = df1.loc[:, cols].groupby(['Road_traffic_density', 'City']).count().reset_index()
    df2.rename(columns = {'ID' : 'ID (count)'}, inplace= True)
    # gerando o gráfico de linhas e armazenando-o em 'fig'
    fig = (px.scatter(df2, x = 'Road_traffic_density', y = 'City', 
                      size = 'ID (count)', labels = {'ID (count)': 'Pedidos registrados', 
                               'City' : 'Cidade', 'Road_traffic_density' : 'Densidade do tráfego'}))
    return fig

def traffic_order_share(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar uma imagem contendo os elementos de um gráfico de pizza.
    
        Dados de interesse:
        1. Coluna dos IDs das entregas;
        2. Coluna das condições de trânsito.

        Objetivo do gráfico gerado: Quantificar a porcentagem de pedidos realizados em cada uma das condições de trânsito.

        Input:  Dataframe
        Output: Objeto fig a ser plotado.
    """
    # definindo colunas a serem filtradas
    cols = ['ID', 'Road_traffic_density']
    # filtragem das linhas
    df2 = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df2.rename(columns = {'ID' : 'ID (count)'}, inplace= True)
    df2['Delivery_percents_by_traffic'] = df2['ID (count)']/df2['ID (count)'].sum()
    # gerando o gráfico de linhas e armazenando-o em 'fig'
    fig = px.pie(df2, values = 'Delivery_percents_by_traffic', names = 'Road_traffic_density')
    return fig

def order_by_day(df1):
    """ Esta função tem a responsabilidade de agrupar parte dos dados de um dataframe e gerar uma imagem contendo os elementos de um gráfico de barras.
    
        Dados de interesse:
        1. Coluna dos IDs das entregas;
        2. Coluna das datas em que cada pedido ocorreu.

        Objetivo do gráfico gerado: Relacionar os pedidos realizados por suas respectivas datas.

        Input:  Dataframe
        Output: Objeto fig a ser plotado.
    """
    # definindo colunas a serem filtradas
    cols = ['ID', 'Order_Date']
    # filtragem das linhas
    df2 = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    df2.rename( columns = {'ID':'ID (count)'}, inplace = True)
    # gerando o gráfico de linhas e armazenando-o em 'fig'
    fig = (px.bar(df2, x = 'Order_Date', y= 'ID (count)', labels = {'Order_Date' : 'Data do pedido',
                                                                   'ID (count)': 'Pedidos registrados'}))
    return fig

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

# ==========================================================================================================================
# RESPONDENDO AS QUESTÕES - VISÃO EMPRESA
# ==========================================================================================================================

# ==========================================================================================================================
# BARRA LATERAL NO STREAMLIT
# ==========================================================================================================================
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

# ==========================================================================================================================
# INTEGRANDO OS FILTROS DO STREAMLIT COM OS DADOS
# ==========================================================================================================================

# Aplicando o filtro de data no Dataframe
filtro_data = df1['Order_Date'] <= date_slider

# Aplicando o filtro de condição de tráfego no Dataframe
filtro_trafeg = df1['Road_traffic_density'].isin(traffic_options) 

# Filtrando o Dataframe
df1 = df1.loc[filtro_data & filtro_trafeg, :]

# ==========================================================================================================================
# LAYOUT NO STREAMLIT
# ==========================================================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    
    with st.container():
        # Quantidade de pedidos por dia
        st.header('Pedidos por dia')
        fig = order_by_day(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    st.markdown("""---""")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Quantidade de pedidos por densidade de tráfego
            st.header('Pedidos por densidade de tráfego')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            # Quantidade de pedidos por densidade de tráfego e por cidade
            st.header('Pedidos por densidade de tráfego e cidade')
            fig = city_and_traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width = True)

with tab2:
    with st.container():
        # Quantidade de pedidos por semana
        st.header('Quantidade de pedidos por semana')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    st.markdown("""---""")
    
    with st.container():
        # Quantidade média de pedidos por entregador por semana
        st.header('A quantidade média de pedidos por entregador por semana')
        fig = week_personID_order_share(df1)
        st.plotly_chart( fig, use_container_width = True)

with tab3:
    # Mapa geográfico das localizações centrais dos pedidos
    st.header('Mapa geográfico das localizações centrais dos pedidos')
    order_map(df1)

st.markdown("""---""") 