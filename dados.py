
import pandas as pd
import streamlit as st
from streamlit_modal import Modal
import phonenumbers
import plotly.express as px
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, firestore

# Configuração da página do Streamlit
st.set_page_config("Participantes", page_icon="👟", layout="centered")

# Função para carregar dados do Firestore
def carregar_dados_firestore():
    try:
        key_dict = st.secrets["textkey"]
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds)

        inscritos_ref = db.collection("inscritos").stream()
        dados = [doc.to_dict() for doc in inscritos_ref]
        return pd.DataFrame(dados) if dados else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firestore: {e}")
        return pd.DataFrame()

# Exemplo de uso
if __name__ == "__main__":
    df = carregar_dados_firestore()
    


# Modal de login
def show_login_modal():
    modal = Modal("Login 🔐", key="popup")
    if modal.is_open():
        with modal.container():
            st.title("Painel Administrativo🔑")
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
                                       ("participou_ultima_corrida", "Participação na Última Corrida", ["#E22A2A", "#02640C"])]:
                st.header(title)
                dados_agrupados = dados.groupby(col).size().reset_index(name="quantidade")
                fig = gerar_grafico(dados_agrupados, eixo_x=col, eixo_y="quantidade",
                                    titulo=title, cor=col, labels={col: title, "quantidade": "Quantidade"},
                                    cores_personalizadas=color)
                st.plotly_chart(fig)
            
        else:
            st.warning("Nenhum dado encontrado no Firestore.")
