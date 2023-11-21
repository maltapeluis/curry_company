import streamlit as st
from PIL import Image

st.set_page_config(
    layout = 'wide',
    page_title = 'Home')

image_path = 'images/logo.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width = 240)

# Textos a serem exibidos na barra lateral
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('## Curry Company Growth Dashboard')
st.markdown(
    """
    Este Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas globais de comportamento. 
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Empresa:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Empresa:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Necessita ajuda?
        Powered by linkedin.com/in/maltape/
    """)
    