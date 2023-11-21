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
st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')

# Definindo o título da página a ser exibido
st.title('Marketplace - Visão Restaurantes')

# ==========================================================================================================================
# FUNÇÕES
# ==========================================================================================================================
def time_metric(df1, metric, fest):
    """ Esta função tem como responsabilidade calcular e informar a média ou o desvio padrão do tempo de realização das entregas do conjunto de dados, durante a ocorrência do Festival ou não.   

        Input:  1. Dataframe;
                2. O tipo de métrica desejada - metric = 'Avg_time' ou 'Std_time';
                3. Com ou sem a ocorrência do Festival - fest = 'Yes' ou 'No'.
        Output: Um valor de média ou desvio padrão do tempo de duração das entregas.
    """
    if metric in ['Avg_time', 'Std_time']:
        cols = ['Time_taken(min)', 'Festival']
        df2 = df1.loc[:, cols].groupby('Festival').agg(['mean', 'std']).reset_index()
        
        df2.columns = ['Festival', 'Avg_time', 'Std_time']
                                
        if fest in ['Yes', 'No']:
            filtro = df2['Festival'] == fest
        else:
            raise ValueError("Invalid parameter for 'fest' parameter! Expected 'Yes' or 'No'.")
        
        resultado = df2.loc[filtro, metric].round(1)
        return resultado    
    
    else:
        raise ValueError("Invalid parameter for 'metric' parameter! Expected 'Avg_time' or 'Std_time'.")

def distance(df1, kind):
    """ Esta função tem como responsabilidade calcular e informar a distância média entre as localizações dos restaurantes e os pontos de entrega de todo o conjunto de dados ou gerar um gráfico de pizza que referencia as cidades com as respectivas distribuições desta distância.   

        Input:  1. Dataframe;
                2. O tipo de saída desejada - kind = 'fig' para gerar a figura de um gráfico de pizza ou 'med' para gerar a métrica de média.
        Output: 1. A figura de um gráfico de pizza;
                2. A métrica de média.
    """
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        
    df2 = df1.copy()
    df2['Distance'] = (df2.loc[:, cols].apply( lambda x:
                                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                                          axis = 1))
        
    if kind == 'fig':
        df3 = df2.loc[:, ['Distance', 'City']].groupby('City').mean().reset_index()
        
        df3.rename(columns = {'Distance' : 'Distance (mean)'}, inplace = True)
        
        fig = px.pie(df3, values = 'Distance (mean)', names = 'City')
        return fig
    elif kind == 'med':
        dist_med = float('{:.2f}'.format(df2['Distance'].mean()))
        return dist_med 
    else:
        raise ValueError("Invalid parameter for 'kind' parameter! Expected 'fig' or 'med'.")

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
# RESPONDENDO AS QUESTÕES - VISÃO RESTAURANTES
# =========================================

# =========================================
# BARRA LATERAL NO STREAMLIT
# =========================================
image_path = ('images/logo.jpg')
image = Image.open( image_path)
st.sidebar.image( image, width = 240)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Período a ser analisado:')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime( 2022, 4, 6),
    min_value = datetime( 2022, 2, 11),
    max_value = datetime( 2022, 4, 6),
    format = 'DD-MM-YYYY',
    label_visibility='hidden')

st.sidebar.markdown("""---""")

city_options = st.sidebar.multiselect(
    'Quais as cidades de interesse?',
    ['Urban', 'Metropolitian', 'Semi-Urban'],
    default = ['Urban', 'Metropolitian', 'Semi-Urban'],)

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'],)

climate_options = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])
    
st.sidebar.markdown("""---""")
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

# Aplicando o filtro de cidades no Dataframe
filtro_cidade = df1['City'].isin(city_options)

# Aplicando o filtro de condição do trânsito no Dataframe
filtro_trafeg = df1['Road_traffic_density'].isin(traffic_options) 

# Aplicando o filtro de condição de clima  no Dataframe
filtro_clima = df1['Weatherconditions'].isin(climate_options) 

# Filtrando o Dataframe
df1 = df1.loc[filtro_data & filtro_trafeg & filtro_clima & filtro_cidade, :]

# =========================================
# LAYOUT NO STREAMLIT
# =========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.header('Métricas Globais')

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            entreg_unic = df1.Delivery_person_ID.nunique()
            
            st.markdown('Entregadores únicos')
            col1.metric('Entregadores únicos', entreg_unic, label_visibility = 'hidden')
        with col2:
            dist_med = distance(df1, 'med')
            
            st.markdown('Distância média (km)')
            col2.metric('Distância média (km)', dist_med, label_visibility = 'hidden')           
        with col3:
            resultado = time_metric(df1, 'Avg_time', 'Yes')
            
            st.markdown('Tempo de entrega médio com o Festival (min)')
            col3.metric('Tempo de entrega médio com o Festival (min)', resultado, label_visibility = 'collapsed')
        
        with col4:
            resultado = time_metric(df1, 'Std_time', 'Yes')
            
            st.markdown('O desvio padrão médio das entregas com o Festival')
            col4.metric('O desvio padrão médio das entregas com o Festival', resultado, label_visibility = 'collapsed')
           
        with col5:
            resultado = time_metric(df1, 'Avg_time', 'No')
            
            st.markdown('Tempo de Entrega médio sem o Festival (min)')
            col5.metric('Tempo de Entrega médio sem o Festival (min)', resultado, label_visibility = 'collapsed')
            
        with col6:
            resultado = time_metric(df1, 'Std_time', 'No')
            
            st.markdown('O desvio padrão médio das entregas sem o Festival')
            col6.metric('O desvio padrão médio das entregas sem o Festival', resultado, label_visibility = 'collapsed')

        st.markdown("""---""")
    
    with st.container():
        st.header('Distribuição Distância X Cidade')
        fig = distance(df1, 'fig')
        st.plotly_chart(fig, use_container_width = True)

    st.markdown("""---""")
    with st.container():
        st.header('Distribuição do Tempo')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Tempo X Cidade')

            cols = ['Time_taken(min)', 'City']

            df2 = df1.loc[:, cols].groupby('City').agg(['mean', 'std']).reset_index()
            df2.columns = ['City','Avg_time', 'Std_time']
            
            fig = go.Figure()
            fig.add_trace( go.Bar( name = 'Control',
                                  x = df2['City'],
                                   y = df2['Avg_time'],
                                   error_y = dict( type = 'data', array = df2['Std_time'])))
            
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('##### Tempo X Tipo de Entrega')

            cols = ['Time_taken(min)', 'City', 'Type_of_order']

            df2 = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg(['mean', 'std']).reset_index()
            df2.columns = ['Cidade', 'Tipo de Pedido', 'Média do tempo (min)', 'Desvio Padrão do tempo']

            st.dataframe(df2)
            
    with st.container():
        st.header('Tempo X Cidade X Condição do Trânsito')

        cols = ['Time_taken(min)', 'City', 'Road_traffic_density']

        df2 = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg(['mean', 'std']).reset_index()
        df2.columns = ['Cidade', 'Condição do Trânsito', 'Média do tempo (min)', 'Desvio Padrão do tempo']
        
        fig = px.sunburst(df2, path = ['Cidade', 'Condição do Trânsito'],
                          values = 'Média do tempo (min)',
                          color = 'Desvio Padrão do tempo',
                          color_continuous_scale = 'RdBu',
                          color_continuous_midpoint = np.average(df2['Desvio Padrão do tempo']))
        
        st.plotly_chart(fig, use_container_width = True)
    st.markdown("""---""")