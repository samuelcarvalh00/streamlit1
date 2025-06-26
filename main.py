import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt
from datetime import datetime,timedelta
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');

.stApp {    
    background-image: url('https://i.pinimg.com/736x/66/93/18/669318c401c3c9b6f6f8ffd940df29f9.jpg');
    background-repeat: no-repeat;
    background-size: cover;
    color: #FFFFFF;
}

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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Funções de carregamento de dados
@st.cache_data # Cache por 1 hora
def carregar_dados(empresas, start="2010-01-01", end=None):
    if end is None:
        end = datetime.today().strftime('%Y-%m-%d')
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start=start, end=end)
    cotacoes_acao = cotacoes_acao["Close"]
    print(cotacoes_acao.columns)

    return cotacoes_acao


@st.cache_data
def carregar_tickers_acoes():
        base_tickers = pd.read_csv("IBOV.csv", sep=";")
        tickers = list(base_tickers["Código"])
        tickers = [item + ".SA" for item in tickers]
        return tickers
  

# Carregar tickers
acoes = carregar_tickers_acoes()
if not acoes:
    st.error("Nenhum ticker carregado. Verifique o arquivo IBOV.csv.")
    st.stop()

# Carregar dados
with st.spinner("Carregando dados..."):
    dados = carregar_dados(acoes)

# Verificar se dados foram carregados
if dados.empty:
    st.error("Nenhum dado disponível para os tickers selecionados.")
    st.stop()

# Interface do Streamlit
st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos
""")

# Filtros na barra lateral
st.sidebar.header("Filtros")

# Filtro de ações
lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar", dados.columns,)
if lista_acoes:
    dados = dados[lista_acoes]
else:
    st.warning("Nenhuma ação selecionada. Mostrando todas as ações disponíveis.")

# Filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider(
    "Selecione o período",
    min_value=data_inicial,
    max_value=data_final,
    value=(data_inicial, data_final),
    step=timedelta(days=1)
)

# Filtrar dados pelo período
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# Criar o gráfico
st.line_chart(dados)

# Cálculo de performance
texto_performance_ativos = ""
if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)

carteira = [1000 for _ in lista_acoes]  # Inicializa a carteira com 1000 para cada ação
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

