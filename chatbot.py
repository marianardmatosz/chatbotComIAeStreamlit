import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIConnectionError


load_dotenv()

st.set_page_config(page_title="Assistente Bella Moda")
st.title("Assistente Virtual Bella Moda 🛍️")
st.caption("Atendimento automático - Moda e Acessórios")

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    st.error("Chave 'DEEPSEEK_API_KEY' não encontrada no arquivo .env!")
    st.stop()


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=60.0  
)

INSTRUCOES = """
Você é um assistente virtual da loja Bella Moda, uma loja de roupas e acessórios de Porto Alegre/RS.

Informações da loja:
- Horário: seg a sex das 9h às 19h, sáb das 9h às 13h.
- Produtos: camisetas (R$ 49,90), calças (R$ 129,90)
e tênis (R$ 199,90).
- Trocas: até 30 dias, com nota fiscal e etiqueta.
- Pagamento: Pix (5% de desconto), cartão em até 10x.
- Frete grátis para a região metropolitana.

Regras de comportamento:
- Seja simpático, breve e use linguagem simples.
- Responda APENAS assuntos relacionados à loja.
- Se perguntarem sobre outros assuntos, diga educadamente
que só pode ajudar com temas da Bella Moda.
- Nunca invente informações que não estão acima; em caso de
dúvida, oriente a falar com um atendente humano
- Quando a pessoa agradecer, responda com por exemplo:
"Não há de quê! Bella Moda: Vista-se de confiança!" """


if "historico" not in st.session_state:
    st.session_state.historico = [
        {"role": "system", "content": INSTRUCOES}
    ]


for mensagem in st.session_state.historico:
    if mensagem["role"] != "system":
        with st.chat_message(mensagem["role"]):
            st.write(mensagem["content"])


pergunta = st.chat_input("Digite sua mensagem...")

if pergunta:

    with st.chat_message("user"):
        st.write(pergunta)
    st.session_state.historico.append({"role": "user", "content": pergunta})


    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Você é uma assistente virtual simpática da loja Bella Moda, especialista em moda e acessórios."},
                    *st.session_state.historico
                ],
                stream=True,  
            )
         
            resposta = st.write_stream(stream)
            st.session_state.historico.append({"role": "assistant", "content": resposta})

        except APITimeoutError:
            st.error("O servidor do DeepSeek demorou para responder. Por favor, tente novamente em alguns instantes.")
        except APIConnectionError:
            st.error("Falha de conexão com a API. Verifique sua conexão com a internet.")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")


st.sidebar.metric("Total de mensagens", len(st.session_state.historico))

if st.sidebar.button("Limpar histórico"):
    st.session_state.historico = []
    st.rerun()

fluxo = client.chat.completions.create(
    model="deepseek-chat",
    messages=st.session_state.historico,
    stream=True
    )

with st.chat_message("assistant"):
    resposta = st.write_stream(fluxo)

st.session_state.historico.append(
    {"role": "assistant", "content": resposta})