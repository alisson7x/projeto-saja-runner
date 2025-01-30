import os
import json
import pandas as pd
import streamlit as st
from streamlit_modal import Modal
import phonenumbers
import plotly.express as px
from google.cloud import firestore
from google.oauth2 import service_account

# Configuração da página do Streamlit
st.set_page_config("Participantes", page_icon="👟", layout="centered")

# Função para carregar dados do Firestore
def carregar_dados_firestore():
    try:
        # Conecta ao Firestore
        key_dict = json.loads(st.secrets["textkey"])
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds)

        # Recupera todos os documentos da coleção "inscritos"
        inscritos_ref = db.collection("inscritos").stream()
        dados = []

        for doc in inscritos_ref:
            dados.append(doc.to_dict())

        # Converte os dados para um DataFrame do Pandas
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firestore: {e}")
        return pd.DataFrame()

# Exibe o modal de login
def show_login_modal():
    modal = Modal("Login 🔐", key="popup")
    if modal.is_open():
        with modal.container():
            st.title("Olá runner! 👟")
            password = st.text_input("Digite sua senha:", type="password")
            if st.button("Login"):
                if password == "corrida":
                    st.success("Login bem-sucedido!")
                    st.session_state.logged_in = True
                    modal.close()
                else:
                    st.error("Senha incorreta. Tente novamente.")
    modal.open()

# Formata números de telefone
def format_phone_number(phone):
    try:
        parsed_phone = phonenumbers.parse(str(phone), "BR")
        return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        return phone

# Gera gráficos com Plotly
def gerar_grafico(dados, eixo_x, eixo_y, titulo, cor, labels, cores_personalizadas=None):
    fig = px.bar(
        dados,
        x=eixo_x,
        y=eixo_y,
        title=titulo,
        color=cor,
        labels=labels,
        color_discrete_sequence=cores_personalizadas or px.colors.qualitative.Safe
    )
    fig.update_traces(texttemplate='%{y}', textposition='inside')
    return fig

# Inicializa a variável de estado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Mostra o modal de login, se necessário
if not st.session_state.logged_in:
    show_login_modal()

# Exibe os dados apenas se o usuário estiver logado
if st.session_state.logged_in:
    st.info("Apenas organizadores têm acesso a essa página!", icon="🪪")

    # Carrega os dados do Firestore
    dados = carregar_dados_firestore()

    if not dados.empty:
        # Exibe informações gerais
        st.header(f"{len(dados)} pessoas estão cadastradas para a corrida.")
        st.divider()

        # Exibe tabela de participantes
        st.header("Participantes", help="Apenas organizadores podem ver esses dados!")
        st.dataframe(dados)
        st.divider()

        # Quantidade de pessoas por cidade
        st.header("Quantidade de Pessoas por Cidade")
        dados_agrupados_cidade = dados.groupby('cidade').size().reset_index(name='quantidade')
        fig_cidade = gerar_grafico(
            dados_agrupados_cidade,
            eixo_x='cidade',
            eixo_y='quantidade',
            titulo='Quantidade de Pessoas por Cidade',
            cor='cidade',
            labels={'cidade': 'Cidades', 'quantidade': 'Quantidade de Pessoas'}
        )
        st.plotly_chart(fig_cidade)
        st.divider()

        # Quantidade de pessoas por sexo
        st.header("Quantidade de Pessoas por Sexo")
        dados_agrupados_sexo = dados.groupby("sexo").size().reset_index(name="quantidade")
        fig_sexo = gerar_grafico(
            dados_agrupados_sexo,
            eixo_x='sexo',
            eixo_y='quantidade',
            titulo='Quantidade de Pessoas por Sexo',
            cor='sexo',
            labels={'sexo': 'Sexo', 'quantidade': 'Quantidade de Pessoas'},
            cores_personalizadas=['#EF553B', '#636EFA']
        )
        st.plotly_chart(fig_sexo)
        st.divider()

        # Análise de participação na última corrida
        st.header("Análise de Participantes desde a Última Corrida")
        dados_agrupados_corrida = dados.groupby("part_ultima_corrida").size().reset_index(name="quantidade")
        fig_corrida = gerar_grafico(
            dados_agrupados_corrida,
            eixo_x='part_ultima_corrida',
            eixo_y='quantidade',
            titulo='Participação na Última Corrida',
            cor='part_ultima_corrida',
            labels={'part_ultima_corrida': 'Última Corrida', 'quantidade': 'Quantidade de Pessoas'},
            cores_personalizadas=['#E22A2A', '#02640C']
        )
        st.plotly_chart(fig_corrida)

        # Contagem explícita de participantes
        quantidade_nao = dados_agrupados_corrida.loc[dados_agrupados_corrida['part_ultima_corrida'] == 'Não', 'quantidade'].sum()
        quantidade_sim = dados_agrupados_corrida.loc[dados_agrupados_corrida['part_ultima_corrida'] == 'Sim', 'quantidade'].sum()
        st.subheader(f"{quantidade_nao} pessoas não participaram da última corrida❌")
        st.subheader(f"{quantidade_sim} pessoas participaram da última corrida✅")
        st.divider()
    else:
        st.warning("Nenhum dado encontrado no Firestore.")
