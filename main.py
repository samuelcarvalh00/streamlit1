import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');


.stApp {    
    background-image: url('https://i.pinimg.com/736x/66/93/18/669318c401c3c9b6f6f8ffd940df29f9.jpg');
     background-repeat: no-repeat;
     background-size: cover;
    color: #FFFFFF;
    
h1 {
    color: #FFFFFF;
    font-size: 2.5em;
    font-family: "Michroma", sans-serif;
}
h3 {
    color: #FFFFFF;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF;
    color: #757575;
    border-radius: 4rem;
}

[data-testid="stSidebar"] {
    background-color: #2F2F2F;
    color: #757575;
}
stline_chart {
    background-color: #FFFFFF;
    color: #757575;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)



st.write("""
# Preço das ações:
""")

# Adicionando widgets na barra lateral

with st.sidebar:
    st.write("""### Selecione uma ação e o período para visualizar a evolução do preço:""")
    ticker = st.selectbox("Escolha a ação:", ["ITUB4.SA", "PETR4.SA", "VALE3.SA", "BBDC4.SA"], key="ticker")
    periodo = st.selectbox("Escolha o período:", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"], key="periodo")
    cor_linha = st.color_picker("Cor da linha", "#27360A")
    cor_fundo = st.color_picker("Cor do fundo", "#1E1E1E")
    cor_texto = st.color_picker("Cor dos números", "#FFFFFF")
    altura = st.slider("Altura do gráfico", 200,800,400)

@st.cache_data
def carregar_dados(empresa, start="2008-01-01", end="2025-10-01"):
    dados_acao = yf.Ticker(empresa)
    cotacoes_acao = dados_acao.history(period=periodo, start=start, end=end)
    return cotacoes_acao[["Close"]]

# Carregar dados
dados = carregar_dados(ticker)
dados_para_grafico = dados.reset_index()

# Gráfico simples com cor personalizada
grafico = alt.Chart(dados_para_grafico).mark_line(color=cor_linha).encode(
    x='Date',
    y='Close'
).properties(  # Largura automática
    height=altura       # ← Altura personalizada
).configure(
    background=cor_fundo
).configure_axis(
    labelColor=cor_texto,
    titleColor=cor_texto
)

st.altair_chart(grafico, use_container_width=True)


