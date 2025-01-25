import pandas as pd
import streamlit as st
from streamlit_modal import Modal
import phonenumbers
import matplotlib.pyplot as plt
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração de autenticação
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\sombr\\OneDrive\\Documentos\\CredenciaisJSON\\saja-runner-4bc678623cbd.json", scope)

client = gspread.authorize(creds)

st.set_page_config("Participantes", page_icon="👟", layout="centered")

# Inicializa a variável de estado no Streamlit
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Função para mostrar o modal de login
def show_login_modal():
    modal = Modal(f"Login🔐", key="popup")
    with modal.container():
        st.title("Olá runner!👟")
        # Campo de entrada para a senha
        password = st.text_input("Digite sua senha:", type="password")

        if st.button("Login"):
            if password == "corrida":
                st.success("Login bem-sucedido!")
                st.session_state.logged_in = True
                modal.close()  # Fecha o modal após o login bem-sucedido
            else:
                st.error("Senha incorreta. Tente novamente.")

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
    
    # Acessando a planilha
    sheet = client.open("SajaRunner").sheet1
    
    # Leitura de dados da planilha
    dados = pd.DataFrame(sheet.get_all_records())  # Converter para DataFrame
    st.header(f"{len(dados)} pessoas estão cadastradas para a corrida.")

    st.divider()

    # Tabela com os dados dos participantes.
    st.header("Participantes", help="Apenas organizadores podem ver esses dados!")
    st.dataframe(dados)

    st.divider()

    st.header("Quantidade de Pessoas por Cidade")
    # Agrupar os dados por cidade e contar o número de pessoas em cada cidade
    dados_agrupados = dados.groupby('cidade').size().reset_index(name='quantidade')

    # Criar o gráfico interativo usando Plotly
    fig = px.bar(dados_agrupados, x='cidade', y='quantidade', title='Quantidade de Pessoas por Cidade',
                 color="cidade", labels={'cidade': 'Cidades', 'quantidade': 'Quantidade de Pessoas'})

    # Linha que adiciona rótulos de dados dentro das barras
    fig.update_traces(texttemplate='%{y}', textposition='inside')

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)

    st.divider()

    st.header("Quantidade de Pessoas por Sexo")
    # Agrupar os dados por sexo e contar o número de pessoas em cada sexo
    dados_agrupados_sexo = dados.groupby("sexo").size().reset_index(name="quantidade")

    # Criar o gráfico interativo usando Plotly
    fig_sexo = px.bar(dados_agrupados_sexo, x='sexo', y='quantidade', title='Quantidade de Pessoas por Sexo',
                      color="sexo", labels={'sexo': 'Sexo', 'quantidade': 'Quantidade de Pessoas'},
                      color_discrete_sequence=['#EF553B', '#636EFA'])

    # Linha que adiciona rótulos de dados dentro das barras
    fig_sexo.update_traces(texttemplate='%{y}', textposition='inside')

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_sexo)

    st.divider()

    st.header("Análise de Participantes desde a Última Corrida")
    # Agrupar os dados por participação na última corrida
    dados_agrupados_corrida = dados.groupby("ultima_corrida").size().reset_index(name="quantidade")

    # Criar o gráfico interativo usando Plotly
    fig_corrida = px.bar(dados_agrupados_corrida, x='ultima_corrida', y='quantidade',
                         title='Quantidade de Pessoas que Participaram ou Não da Última Corrida',
                         color="ultima_corrida", labels={'ultima_corrida': 'Última Corrida',
                                                          'quantidade': 'Quantidade de Pessoas'},
                         color_discrete_sequence=['#E22A2A', '#02640C'])

    # Adicionar rótulos de dados
    fig_corrida.update_traces(texttemplate='%{y}', textposition="inside")

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig_corrida)

    # Filtrando quantidade de "Sim" e "Não" explicitamente
    quantidade_nao = dados_agrupados_corrida.loc[dados_agrupados_corrida['ultima_corrida'] == 'Não', 'quantidade'].sum()
    quantidade_sim = dados_agrupados_corrida.loc[dados_agrupados_corrida['ultima_corrida'] == 'Sim', 'quantidade'].sum()

    # Exibir os resultados no Streamlit
    st.subheader(f"{quantidade_nao} pessoas não participaram da última corrida❌")
    st.subheader(f"{quantidade_sim} pessoas participaram da última corrida✅")

    st.divider()
