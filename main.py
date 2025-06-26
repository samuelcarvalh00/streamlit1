import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from datetime import datetime,timedelta
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap'); 

div.stApp {
    font-family: 'Michroma', sans-serif !important;
    background-image: url('https://i.pinimg.com/736x/66/93/18/669318c401c3c9b6f6f8ffd940df29f9.jpg') !important;
    background-repeat: no-repeat !important;
    background-size: cover !important;
    color: #FFFFFF !important;
}

h1 {
    font-family: 'Michroma', sans-serif !important;
    color: #FFFFFF !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background-color: #4B0082 !important;
    color: #1C0034 !important;
    border-radius: 4rem !important;
}

[data-testid="stSidebar"] {
    background-color: rgba(28, 0, 52, 0.5) !important;
    color: #FFFFFF !important;
}
p{
color: #FFFFFF !important;
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: rgba(28, 0, 52, 0.6) !important; 
    color: #FFFFFF !important; /* Texto branco */
    border-radius: 0.5rem !important; 
    padding: 0.2rem 0.6rem !important; 
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# criar as funções de carregamento de dados
    # Cotações do Itau - ITUB4 - 2010 a 2024

def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-07-01")
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = list(base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()[:20]
dados = carregar_dados(acoes)

# criar a interface do streamlit
st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos
""") # markdown

# prepara as visualizações = filtros
st.sidebar.header("Filtros")

# filtro de acoes
lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})
        
# filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o período", 
                                   min_value=data_inicial, 
                                   max_value=data_final,
                                   value=(data_inicial, data_final),
                                   step=timedelta(days=1))

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# criar o grafico
st.line_chart(dados)


# calculo de perfomance
texto_performance_ativos = ""

if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes)==1:
    dados = dados.rename(columns={"Close": acao_unica})


carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo)

    if performance_ativo > 0:
        # :cor[texto]
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: {performance_ativo:.1%}"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :green[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da carteira com todos os ativos: {performance_carteira:.1%}"



st.write(f"""
### Performance dos Ativos
Essa foi a perfomance de cada ativo no período selecionado:

{texto_performance_ativos}

{texto_performance_carteira}
""")
