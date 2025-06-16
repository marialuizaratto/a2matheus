import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Afinidade Legislativa", layout="centered")

st.title("📊 Afinidade Legislativa com Deputados Federais")
st.write("""
Este aplicativo compara suas opiniões com votações reais da Câmara dos Deputados.

A partir das suas respostas, identificamos quais deputados do seu estado votam de forma mais alinhada com você.
""")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("votos_camara.csv")
    return df

df = carregar_dados()

# Perguntas associadas a cada id de votação
perguntas = {
    "2453934-65": "Você concorda com o PL das fake news?",
    "2236291-85": "Você apoia o novo arcabouço fiscal (substituição do teto de gastos)?"
    # Adicione mais PLs conforme o seu CSV
}

ufs_disponiveis = sorted(df["uf"].dropna().unique())
uf_usuario = st.selectbox("Escolha seu estado (UF):", ufs_disponiveis)

respostas_usuario = {}
opcoes_resposta = ["Discordo muito", "Discordo", "Neutro", "Concordo", "Concordo muito"]

st.subheader("📋 Suas respostas")

for id_vot, pergunta in perguntas.items():
    resposta = st.radio(pergunta, opcoes_resposta, key=id_vot)
    respostas_usuario[id_vot] = resposta

pesos_usuario = {
    "Discordo muito": -2,
    "Discordo": -1,
    "Neutro": 0,
    "Concordo": 1,
    "Concordo muito": 2
}

def buscar_wikipedia(nome):
    url = f"https://pt.wikipedia.org/wiki/{nome.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "Não foi possível encontrar uma descrição na Wikipedia."

        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafo = soup.select_one("p")

        if paragrafo and paragrafo.text.strip():
            return paragrafo.text.strip()
        else:
            return "Página encontrada, mas sem resumo disponível."

    except Exception as e:
        return f"Erro ao acessar Wikipedia: {e}"

if st.button("Ver afinidade com deputados do seu estado"):
    st.subheader("🏆 Pódio de afinidade legislativa")

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

    ranking = sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True)

    if ranking:
        for i, (dep, score) in enumerate(ranking[:3], 1):
            st.write(f"{i}º lugar: {dep} — {score} pontos")

        dep_vencedor = ranking[0][0]
        nome_vencedor = dep_vencedor.split(" (")[0]

        st.subheader(f"🧾 Quem é {nome_vencedor}?")
        descricao = buscar_wikipedia(nome_vencedor)
        st.write(descricao)

        st.subheader(f"📌 Como {nome_vencedor} votou nas questões:")
        votos_vencedor = df[(df["nome"] == nome_vencedor) & (df["uf"] == uf_usuario)]

        for id_vot, pergunta in perguntas.items():
            voto_linha = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]
            voto_final = voto_linha["voto"].iloc[0] if not voto_linha.empty else "Sem registro"
            st.markdown(f"- **{pergunta}** → {voto_final}")
    else:
        st.info("Nenhum deputado encontrado para esse estado.")

