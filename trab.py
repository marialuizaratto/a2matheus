import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Afinidade Legislativa", layout="centered")

st.title("📊 Afinidade Legislativa com Deputados Federais")

st.markdown("""
Este aplicativo compara suas opiniões com votações reais da Câmara dos Deputados.

A partir das suas respostas, identificamos quais deputados **do seu estado** votam de forma mais alinhada com você.

### 🧠 Como funciona o sistema de pontos:

- Se você **concorda muito** e o deputado votou **Sim**, ele ganha **+2 pontos**.
- Se você **discorda muito** e o deputado votou **Não**, também ganha **+2 pontos**.
- Se o voto do deputado for o oposto da sua opinião, ele perde pontos.
- Votos "Abstenção", "Obstrução", etc. contam como **neutros** (0 ponto).

No final, mostramos um ranking de quem mais se alinha com você!
""")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("votos_camara.csv")
    return df

df = carregar_dados()

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

def buscar_wikipedia_info(nome):
    busca = f"deputado {nome}"
    url = f"https://pt.wikipedia.org/wiki/{busca.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafo = soup.select_one("p")
        img = soup.select_one("table.infobox img")

        resumo = paragrafo.text.strip() if paragrafo else "Sem resumo disponível."
        imagem_url = f"https:{img['src']}" if img else None

        return resumo, imagem_url

    except Exception:
        return None, None

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
        resumo, imagem_url = buscar_wikipedia_info(nome_vencedor)

        if imagem_url:
            st.image(imagem_url, width=200)
        if resumo:
            st.write(resumo)
        else:
            st.write("Não foi possível encontrar uma descrição.")

        st.subheader(f"📌 Como {nome_vencedor} votou nas questões:")
        votos_vencedor = df[(df["nome"] == nome_vencedor) & (df["uf"] == uf_usuario)]

        for id_vot, pergunta in perguntas.items():
            voto_linha = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]
            voto_final = voto_linha["voto"].iloc[0] if not voto_linha.empty else "Sem registro"

            peso_usuario = pesos_usuario[respostas_usuario[id_vot]]
            if voto_final == "Sim":
                peso_dep = 1
            elif voto_final == "Não":
                peso_dep = -1
            else:
                peso_dep = 0

            if peso_usuario == 0 or peso_dep == 0:
                cor = "gray"
            elif peso_usuario == peso_dep or peso_usuario * peso_dep > 0:
                cor = "green"
            else:
                cor = "red"

            st.markdown(
                f'<span style="color:{cor}">• <b>{pergunta}</b> → {voto_final}</span>',
                unsafe_allow_html=True
            )
    else:
        st.info("Nenhum deputado encontrado para esse estado.")

