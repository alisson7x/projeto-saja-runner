import streamlit as st
import pandas as pd
from streamlit_modal import Modal
import phonenumbers
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config("Saja Runner", page_icon="👟", layout="centered")

# Configuração de autenticação para Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("saja-runner_credenci.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("SajaRunner").sheet1
except Exception as e:
    st.error(f"Erro na configuração do Google Sheets: {e}")
    st.stop()

# Título
st.title("Bem-vindo ao Sistema de Cadastro para a corrida do Saja Runner!👟")
st.divider()

# Adicionando imagem
st.image("img_zap.jpeg", width=700)
st.divider()

# Função para salvar os dados na Google Sheets
def salvar_dados(sheet, nome, idade, telefone, cidade, sexo, part_ultima_corrida):
    try:
        sheet.append_row([nome, idade, telefone, cidade, sexo, part_ultima_corrida])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar os dados: {e}")
        return False

# Validação de entradas
def validar_dados(nome, idade, telefone, cidade, sexo, part_ultima_corrida):
    if not nome or not idade or not telefone or not cidade or not sexo or not part_ultima_corrida:
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

# Coletar os dados do usuário
nome = st.text_input("Digite seu nome:", help="Escreva seu nome completo").title()
idade = st.text_input("Digite sua idade:", max_chars=3)
telefone = st.text_input("Digite seu telefone:", max_chars=13, help="Digite seu telefone com o DDD (somente números)")
cidade = st.text_input("Qual sua cidade, comunidade ou povoado?", max_chars=35).title()
sexo = st.radio("Selecione seu sexo:", ["Masculino", "Feminino"], horizontal=True)
part_ultima_corrida = st.radio("Você participou da última corrida e café?", ["Sim", "Não"], horizontal=True)

# Formatar o telefone no padrão internacional
telefone_formatado = ""
if telefone:
    try:
        parsed_phone = phonenumbers.parse(telefone, "BR")
        telefone_formatado = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        telefone_formatado = telefone

# Botão para finalizar cadastro
if st.button("Confirmar"):
    if validar_dados(nome, idade, telefone_formatado, cidade, sexo, part_ultima_corrida):
        if salvar_dados(sheet, nome, idade, telefone_formatado, cidade, sexo, part_ultima_corrida):
            st.success("Parabéns, você se inscreveu no café e corrida de Saja!✅👟")
            st.balloons()

            # Instancia o modal
            modal = Modal(
                f"Parabéns, {nome}!🎉\n\nAgora basta você entrar no nosso grupo para acompanhar todas as notícias e novidades!👟",
                key="popup"
            )
            with modal.container():
                st.button("Entre no grupo do WhatsApp!", on_click=lambda: st.write("[Clique aqui para entrar](https://chat.whatsapp.com/KJWgrjXKjEu4YoDyD4VvZe)"))
        else:
            st.error("Erro ao salvar os dados. Tente novamente.")
