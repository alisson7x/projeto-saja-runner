import pandas as pd
import streamlit as st
from streamlit_modal import Modal
import phonenumbers
import matplotlib.pyplot as plt
import plotly.express as px



st.set_page_config("Participantes", page_icon="👟",
                   layout="centered")

# Inicializa a variável de estado no Streamlit
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Função para mostrar o modal de login
def show_login_modal():
    modal = Modal(f"Login🔐", key="popup")
    with modal.container():
        st.title("Olá runner!👟")
        # Campo de entrada para a senha
        password = st.text_input("digite sua senha:", type="password")

        if st.button("Login"):
            if password == "corrida":
                st.success("Login bem-sucedido!")
                st.session_state.logged_in = True
                modal.close()  # Fecha o modal após o login bem-sucedido
            else:
                st.error("senha incorreta. Tente novamente.")


# Função para formatar números de telefone
def format_phone_number(phone):
    try:
        parsed_phone = phonenumbers.parse(str(phone), "BR")
        formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return formatted_phone
    except phonenumbers.NumberParseException:
        return phone

# Mostra o modal de login se não estiver logado
if not st.session_state.logged_in:
    show_login_modal()

# Verifica se o usuário está logado antes de exibir os dados
if st.session_state.logged_in:
    st.info("Apenas organizadores têm acesso à essa página!", icon="🪪")
    
    #importa o arquivo com os dados dos participantes
    dados = pd.read_csv("dados.csv")
    # Verifique se a coluna "telefone" existe
    if "telefone" in dados.columns:
        # Formata os números de telefone
        dados["telefone"] = dados["telefone"].apply(format_phone_number)
    else:
        st.error("A coluna telefone não foi encontrada no arquivo CSV.")
    
#mostra a quantidade de pessoas cadastradas.
quantidade_pessoas = dados["nome"].count()
st.title(f"{quantidade_pessoas} pessoas estão cadastradas para a corrida.")

st.divider()

# Tabela com os dados dos participantes.
st.header("Participantes", help="Apenas organizadores podem ver esses dados!")
st.dataframe(dados)

st.divider()

st.header("quantidade de pessoas por cidade.")
# Agrupar os dados por Cidade e contar o número de pessoas em cada cidade
dados_agrupados = dados.groupby('cidade').size().reset_index(name='quantidade')

# Calcular a média de pessoas por cidade
media_pessoas = dados_agrupados['quantidade'].mean()

# Criar o gráfico interativo usando Plotly
fig = px.bar(dados_agrupados, x='cidade', y='quantidade', title='quantidade de Pessoas por Cidade',
                color="cidade",
                labels={'cidade': 'Cidades', 'quantidade': 'quantidade de Pessoas'})

# Linha que adiciona rótulos de dados dentro das barras

fig.update_traces(texttemplate='%{y}', textposition='inside')


# Exibir o gráfico no Streamlit
st.plotly_chart(fig)

st.divider()

st.header("quantidade de pessoas por sexo.")
# Agrupar os dados por Cidade e contar o número de pessoas em cada cidade
dados_agrupados = dados.groupby("sexo").size().reset_index(name="quantidade")

# Calcular a média de pessoas por cidade
media_pessoas = dados_agrupados['quantidade'].mean()
#Cores das barras
cores_personalizadas = ['#EF553B', '#636EFA']
# Criar o gráfico interativo usando Plotly
fig = px.bar(dados_agrupados, x='sexo', y='quantidade', title='quantidade de Pessoas por Sexo',
                color="sexo",
                color_discrete_sequence=cores_personalizadas,
                labels={'sexo': 'Sexo', 'quantidade': 'quantidade de Pessoas'})

# Linha que adiciona rótulos de dados dentro das barras
fig.update_traces(texttemplate='%{y}', textposition='inside')

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)

st.divider()

# Gráfico do aumento de inscritos desde a última corrida
st.header("Análise de participantes desde a última corrida.")

# Agrupar os dados por pessoas inscritas desde a última corrida
dados_agrupados = dados.groupby("ultima_corrida").size().reset_index(name="quantidade")

# Calcular a média de pessoas da última corrida
media_pessoas = dados_agrupados['quantidade'].mean()
#cores das barras
cores_personalizadas = ['#E22A2A', '#02640C']

# Criar o gráfico de linha usando Plotly
fig = px.bar(dados_agrupados, x='ultima_corrida', y='quantidade',
            title='quantidade de Pessoas que participaram ou não da última corrida',
            color="ultima_corrida",
            color_discrete_sequence=cores_personalizadas,
            labels={'ultima_corrida': 'Ultima Corrida', 'quantidade': 'quantidade de Pessoas'})

# Adicionar rótulos de dados
fig.update_traces(texttemplate='%{y}', textposition="inside")

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)

# Agrupar para agregar e reavaliar os dados
dados_agrupados = dados.groupby(["ultima_corrida"]).size().reset_index(name="quantidade")

# Filtrando explicitamente quantidade "Sim" e "Não"
quantidade_nao = dados_agrupados.loc[dados_agrupados['ultima_corrida'] == 'Não', 'quantidade'].sum()
quantidade_sim = dados_agrupados.loc[dados_agrupados['ultima_corrida'] == 'Sim', 'quantidade'].sum()

# Exibindo a f-string no Streamlit
st.subheader(f"{quantidade_nao} pessoas não participaram da ultima corrida❌")
st.subheader(f"{quantidade_sim} pessoas participaram da ultima corrida✅")

st.divider()