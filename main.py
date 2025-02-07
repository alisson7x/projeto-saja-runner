import streamlit as st
import phonenumbers
from google.cloud import firestore
from google.oauth2 import service_account
import json
from streamlit_modal import Modal

# Configuração da página
st.set_page_config("Saja Runner", page_icon="👟", layout="centered")

# Logo para acessar a pagina de análise de dados (somente adm)
st.logo("img.png", size="large", link="https://projeto-saja-runner-dados.streamlit.app/")

# Título e imagem
st.title("Faça sua inscrição para a corrida do Saja Runner!👟")
st.divider()
st.image("img_zap.jpeg", width=700)
st.divider()

# Função para validar os dados
def validar_dados(nome, idade, telefone, cidade, sexo, part_ultima_corrida):
    if not all([nome, idade, telefone, cidade, sexo, part_ultima_corrida]):
        st.warning("Por favor, preencha todos os campos obrigatórios.")
        return False

    if not idade.isdigit() or int(idade) <= 0:
        st.warning("Por favor, insira uma idade válida.")
        return False

    try:
        parsed_phone = phonenumbers.parse(telefone, "BR")
        if not phonenumbers.is_valid_number(parsed_phone):
            st.warning("Por favor, insira um telefone válido com DDD.")
            return False
    except phonenumbers.NumberParseException:
        st.warning("Por favor, insira um telefone válido com DDD.")
        return False

    return True

# Função para salvar os dados no Firestore
def salvar_dados_firestore(nome, idade, telefone, cidade, sexo, part_ultima_corrida):
    try:
        # Conecta ao Firestore
        key_dict = st.secrets["textkey"]
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds)

        # Cria um documento com os dados do usuário
        doc_ref = db.collection("inscritos").document()
        doc_ref.set({
            "nome": nome,
            "idade": int(idade),
            "telefone": telefone,
            "cidade": cidade,
            "sexo": sexo,
            "participou_ultima_corrida": part_ultima_corrida,
            "timestamp": firestore.SERVER_TIMESTAMP  # Adiciona um timestamp automático
        })
        return True
    except Exception as e:
        st.error(f"Erro ao salvar os dados no Firestore: {e}")
        return False

# Coletar dados do usuário
nome = st.text_input("Digite seu nome:", help="Escreva seu nome completo").title()
idade = st.text_input("Digite sua idade:", max_chars=3)
telefone = st.text_input("Digite seu telefone:", max_chars=13, help="Digite seu telefone com o DDD (somente números)")
cidade = st.text_input("Qual sua cidade, comunidade ou povoado?", max_chars=35).title()
sexo = st.radio("Selecione seu sexo:", ["Masculino", "Feminino"], horizontal=True)
part_ultima_corrida = st.radio("Você participou da última corrida e café?", ["Sim", "Não"], horizontal=True)

# Formatar o telefone no padrão internacional
telefone_formatado = telefone
if telefone:
    try:
        parsed_phone = phonenumbers.parse(telefone, "BR")
        telefone_formatado = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        telefone_formatado = telefone

# Instancia o modal
modal = Modal("Parabens",key="popup")

if st.button("Confirmar"):
    if validar_dados(nome, idade, telefone_formatado, cidade, sexo, part_ultima_corrida):
        if salvar_dados_firestore(nome, idade, telefone_formatado, cidade, sexo, part_ultima_corrida):
            st.success("Parabéns, você se inscreveu no café e corrida de Saja!✅👟")
            st.balloons()
            
            # Instancia o modal
            modal = Modal(f"Parabéns por se inscrever {nome}🎉",key="popup")
            with modal.container():
                st.subheader(f"Agora basta entrar no link abaixo para entrar no grupo e acompanhar todas as novidades sobre a corrida!")
                st.link_button("LINK DO GRUPO📲" , "https://chat.whatsapp.com/LnwO8dv3ENlBRsjNoHXx2S",
                               use_container_width=True)
                
                st.button("Fechar", on_click=modal.close)
        else:
            st.error("Erro ao salvar os dados. Tente novamente.")
