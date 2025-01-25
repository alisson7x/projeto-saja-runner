import streamlit as st
import pandas as pd
from streamlit_modal import Modal
import phonenumbers
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config("Saja Runner",
                   page_icon="👟",
                   layout="centered")

# Configuração de autenticação para Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\Users\sombr\OneDrive\Documentos\CredenciaisJSON\saja-runner_credenci.json", scope)


client = gspread.authorize(creds)

# Acessando a planilha
sheet = client.open("SajaRunner").sheet1

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

    if not telefone.isdigit() or len(telefone) < 10:
        st.warning("Por favor, insira um telefone válido (somente números).")
        return False

    return True

# Função para formatar números de telefone
def format_phone_number(phone):
    try:
        parsed_phone = phonenumbers.parse(str(phone), "BR")
        formatted_phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return formatted_phone
    except phonenumbers.NumberParseException:
        return phone

# Coletar os dados do usuário
nome = st.text_input(label="Digite seu nome:", help="Escreva seu nome completo",)
nome = nome.title()
idade = st.text_input("Digite sua idade:", max_chars=3)
telefone = st.text_input("Digite seu telefone:", max_chars=12, help="Digite seu telefone com o DDD (somente números)")
cidade = st.text_input("Qual sua cidade, comunidade ou povoado?",
                       max_chars=35)
cidade = cidade.title()
sexo = st.pills("Selecione seu sexo", ["Masculino", "Feminino"])
part_ultima_corrida = st.pills("Você participou da ultima corrida e café?", ["Sim", "Não"])
    
# Formatar o telefone no padrão internacional
telefone_formatado = f"+55{telefone.lstrip('0')}" if telefone else ""

# Botão para finalizar cadastro
if st.button("Confirmar"):
    if validar_dados(nome, idade, telefone, cidade, sexo, part_ultima_corrida):
        if salvar_dados(sheet, nome, idade, telefone_formatado, cidade, sexo, part_ultima_corrida):
            st.success("Parabéns, você se inscreveu no café e corrida de Saja!✅👟")
            st.balloons()

            # Instancia o modal
            modal = Modal(f"""
                          Parabéns {nome}!🎉
                          Agora basta você entrar no nosso grupo
                          para acompanhar todas as notícias e novidades!👟
                          """, key="popup")
            with modal.container():
                st.link_button("Entre no grupo do WhatsApp!", url="https://chat.whatsapp.com/KJWgrjXKjEu4YoDyD4VvZe", use_container_width=True, icon="👟")

        else:
            st.error("Erro ao salvar os dados. Tente novamente.")
