import streamlit as st
import pandas as pd

st.set_page_config(page_title="Recomende seu Deputado", layout="centered")

st.title("🔎 Qual deputado combina com você?")
st.write("Responda às perguntas sobre projetos de lei recentes. No final, mostraremos quais deputados do seu estado mais se alinham com suas opiniões.")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("votos_camara.csv")
    return df

df = carregar_dados()

# ✅ Perguntas associadas a cada votação (id_votacao: texto)
perguntas = {
    "345311-270": "Você concorda com o Marco Temporal para demarcação de terras indígenas?",
    "2438467-47": "Você apoia a criação do Dia Nacional para a Ação Climática?",
    "2207613-167": "Você é contra a privatização de empresas e o aumento de custos no saneamento básico?",
    "264726-144": "Você apoia o aumento de pena para porte ilegal de arma?",
    "604557-205": "Você apoia a Lei do Mar, que regula a exploração sustentável dos recursos marítimos?",
    "2417025-55": "Você concorda que uma pessoa que ganha 2 salários mínimos deve pagar imposto de renda?",
    "2231632-97": "Você concorda que documentos públicos devem usar linguagem acessível?",
    "2345281-63": "Você concorda que mulheres têm direito à cirurgia reparadora das mamas após câncer pelo SUS?",
    "2078693-87": "Você apoia repasses federais mesmo para municípios inadimplentes, se for para combater a violência contra a mulher?",
    "2310025-56": "Você apoia a Lei Aldir Blanc de incentivo à cultura?"
}

# Interface: Estado
ufs_disponiveis = sorted(df["uf"].dropna().unique())
uf_usuario = st.selectbox("Escolha seu estado (UF):", ufs_disponiveis)

# Interface: Perguntas
respostas_usuario = {}
opcoes_resposta = ["Discordo muito", "Discordo", "Neutro", "Concordo", "Concordo muito"]

st.subheader("📋 Suas respostas")

for id_vot, pergunta in perguntas.items():
    resposta = st.radio(pergunta, opcoes_resposta, key=id_vot)
    respostas_usuario[id_vot] = resposta

# Mapeamento de pontuação
pesos_usuario = {
    "Discordo muito": -2,
    "Discordo": -1,
    "Neutro": 0,
    "Concordo": 1,
    "Concordo muito": 2
}

# Cálculo
if st.button("Ver meus deputados mais compatíveis"):
    st.subheader("🎯 Deputados mais compatíveis com você")

    pontuacoes = {}

    for id_vot, resposta_usuario in respostas_usuario.items():
        peso_usuario = pesos_usuario.get(resposta_usuario, 0)
        votos_pl = df[(df["id_votacao"] == id_vot) & (df["uf"] == uf_usuario)]

        for _, linha in votos_pl.iterrows():
            nome = linha["nome"]
            partido = linha["partido"]
            voto_dep = linha["voto"]

            if voto_dep == "Sim":
                peso_dep = 1
            elif voto_dep == "Não":
                peso_dep = -1
            else:
                peso_dep = 0

            compat = peso_usuario * peso_dep
            chave = f"{nome} ({partido})"
            pontuacoes[chave] = pontuacoes.get(chave, 0) + compat

    # Ranking final
    ranking = sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True)

    if ranking:
        for i, (deputado, score) in enumerate(ranking[:5], 1):
            st.write(f"{i}. {deputado} — {score} pontos")
    else:
        st.info("Nenhum deputado encontrado para esse estado e essas votações.")
