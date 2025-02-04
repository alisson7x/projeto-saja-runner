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
        if 'db' not in st.session_state:
            if 'textkey' not in st.secrets:
                st.error("Credenciais do Firestore não encontradas. Verifique o arquivo secrets.toml.")
                return pd.DataFrame()
            
            textkey = st.secrets["textkey"]
            key_dict = json.loads(json.dumps(textkey))
            creds = service_account.Credentials.from_service_account_info(key_dict)
            st.session_state.db = firestore.Client(credentials=creds)

        db = st.session_state.db
        inscritos_ref = db.collection("inscritos").stream()

        # Converte documentos para dicionários e formata timestamp
        dados = []
        for doc in inscritos_ref:
            doc_dict = doc.to_dict()
            
            # Converte timestamp para string se for um objeto Timestamp
            if "timestamp" in doc_dict:
                timestamp = doc_dict["timestamp"]
                if isinstance(timestamp, firestore.Timestamp):
                    doc_dict["timestamp"] = timestamp.to_datetime().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    doc_dict["timestamp"] = str(timestamp)  # Caso não seja um Timestamp, converte para string
            
            # Converte todos os valores para tipos serializáveis
            for key, value in doc_dict.items():
                if isinstance(value, (dict, list)):
                    doc_dict[key] = json.dumps(value)  # Converte dicionários e listas em strings JSON
                elif isinstance(value, firestore.Timestamp):
                    doc_dict[key] = value.to_datetime().strftime("%Y-%m-%d %H:%M:%S")  # Converte Timestamp para string
                elif isinstance(value, bytes):
                    doc_dict[key] = value.decode('utf-8')  # Converte bytes para string
            
            dados.append(doc_dict)
        
        return pd.DataFrame(dados) if dados else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firestore: {e}")
        return pd.DataFrame()
# Modal de login
def show_login_modal():
    modal = Modal("Login 🔐", key="popup")
    if modal.is_open():
        with modal.container():
            st.title("Olá runner! 👟")
            password = st.text_input("Digite sua senha:", type="password")
            if st.button("Login"):
                if password == st.secrets.get("senha_corrida", "corrida"):
                    st.success("Login bem-sucedido!")
                    st.session_state.logged_in = True
                    modal.close()
                else:
                    st.error("Senha incorreta. Tente novamente.")
    else:
        modal.open()

# Formata números de telefone
def format_phone_number(phone):
    if pd.isna(phone) or phone == "":
        return "Não informado"
    try:
        parsed_phone = phonenumbers.parse(str(phone), "BR")
        return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        return "Número inválido"

# Gera gráficos
def gerar_grafico(dados, eixo_x, eixo_y, titulo, cor, labels, cores_personalizadas=None):
    fig = px.bar(
        dados, x=eixo_x, y=eixo_y, title=titulo, color=cor, labels=labels,
        color_discrete_sequence=cores_personalizadas or px.colors.qualitative.Safe
    )
    fig.update_traces(texttemplate='%{y}', textposition='inside')
    return fig

# Inicializa login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_modal()

# Exibe dados se logado
if st.session_state.logged_in:
    st.info("Apenas organizadores têm acesso a essa página!", icon="🫧")
    
    if st.button("Carregar dados"):
        dados = carregar_dados_firestore()
        
        if not dados.empty:
            st.header(f"{len(dados)} pessoas cadastradas para a corrida.")
            st.dataframe(dados)
            
            # Gráficos
            for col, title, color in [("cidade", "Quantidade por Cidade", None),
                                       ("sexo", "Quantidade por Sexo", ["#EF553B", "#636EFA"]),
                                       ("part_ultima_corrida", "Participação na Última Corrida", ["#E22A2A", "#02640C"])]:
                st.header(title)
                dados_agrupados = dados.groupby(col).size().reset_index(name="quantidade")
                fig = gerar_grafico(dados_agrupados, eixo_x=col, eixo_y="quantidade",
                                    titulo=title, cor=col, labels={col: title, "quantidade": "Quantidade"},
                                    cores_personalizadas=color)
                st.plotly_chart(fig)
            
        else:
            st.warning("Nenhum dado encontrado no Firestore.")