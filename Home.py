import streamlit as st
import pandas as pd
import wikipedia
import requests
from bs4 import BeautifulSoup

# Configuração da página — deve ser o primeiro comando streamlit chamado!
st.set_page_config(page_title="Afinidade Legislativa", layout="centered", initial_sidebar_state="expanded")

# Título e explicação
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
    return pd.read_csv("votacoes.csv")  # Certifique-se de ter esse CSV!

df = carregar_dados()

# Perguntas vinculadas às votações
perguntas = {
    "345311-270": "Você concorda com o Marco Temporal para demarcação de terras indígenas? [Saiba mais](https://www.camara.leg.br/noticias/966618-o-que-e-marco-temporal-e-quais-os-argumentos-favoraveis-e-contrarios/#:~:text=Marco%20temporal%20%C3%A9%20uma%20tese,data%20de%20promulga%C3%A7%C3%A3o%20da%20Constitui%C3%A7%C3%A3o.)",
    "2438467-47": "Você apoia a criação do Dia Nacional para a Ação Climática?",
    "2207613-167": "Você é contra a privatização de empresas e o aumento de custos no saneamento básico?",
    "264726-144": "Você apoia o aumento de pena para porte ilegal de arma?",
    "604557-205": "Você apoia a [Lei do Mar](https://www.camara.leg.br/noticias/1163592-camara-aprova-projeto-que-cria-a-lei-do-mar), que regula a exploração sustentável dos recursos marítimos?",
    "2417025-55": "Você concorda que uma pessoa que ganha 2 salários mínimos deve pagar imposto de renda?",
    "2231632-97": "Você concorda que documentos públicos devem usar linguagem acessível?",
    "2345281-63": "Você concorda que mulheres têm direito à cirurgia reparadora das mamas após câncer pelo SUS?",
    "2078693-87": "Você apoia repasses federais mesmo para municípios inadimplentes, se for para combater a violência contra a mulher?",
    "2310025-56": "Você apoia a Lei Aldir Blanc de incentivo à cultura? [Saiba mais](https://www.gov.br/pt-br/noticias/cultura-artes-historia-e-esportes/2020/08/lei-aldir-blanc-de-apoio-a-cultura-e-regulamentada-pelo-governo-federal)"
}

pesos_usuario = {
    "Discordo muito": -2,
    "Discordo": -1,
    "Neutro/Não sei": 0,
    "Concordo": 1,
    "Concordo muito": 2
}

ufs_disponiveis = sorted(df["uf"].dropna().unique())
uf_usuario = st.selectbox("📍 Selecione seu estado:", ufs_disponiveis)

respostas_usuario = {}
st.subheader("🗳️ Suas opiniões sobre os temas abaixo:")

for id_vot, pergunta in perguntas.items():
    st.markdown(f"**{pergunta}**")
    st.markdown("<br>", unsafe_allow_html=True)  # espaçamento extra
    resposta = st.radio("", list(pesos_usuario.keys()), key=id_vot)
    respostas_usuario[id_vot] = resposta

def buscar_wikipedia_info(nome):
    wikipedia.set_lang("pt")
    try:
        resumo = wikipedia.summary(nome, sentences=3)
        url = f"https://pt.wikipedia.org/wiki/{nome.replace(' ', '_')}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        img = soup.select_one("table.infobox img")
        imagem_url = f"https:{img['src']}" if img else None
        return resumo, imagem_url
    except Exception:
        return "Não foi possível encontrar uma descrição.", None

if st.button("🔍 Ver afinidade com deputados"):
    st.subheader("🏆 Pódio de afinidade legislativa")

    deputados_uf = df[df["uf"] == uf_usuario]["nome"].unique()
    ranking = []

    progress = st.progress(0)
    total = len(deputados_uf)
    for i, deputado in enumerate(deputados_uf):
        votos_dep = df[(df["nome"] == deputado) & (df["id_votacao"].isin(perguntas.keys()))]
        score = 0
        for _, row in votos_dep.iterrows():
            id_vot = row["id_votacao"]
            voto_dep = row["voto"]
            voto_usuario = respostas_usuario.get(id_vot)

            peso_usuario = pesos_usuario[voto_usuario]
            if voto_dep == "Sim":
                peso_dep = 1
            elif voto_dep == "Não":
                peso_dep = -1
            else:
                peso_dep = 0

            score += peso_usuario * peso_dep

        ranking.append((deputado, score))
        progress.progress((i + 1) / total)

    progress.empty()

    ranking.sort(key=lambda x: x[1], reverse=True)

    medalhas = ["🥇", "🥈", "🥉"]

    if ranking:
        # Mostrar top 3 com medalhas
        for i, (dep, score) in enumerate(ranking[:3], 1):
            st.write(f"{medalhas[i-1]} {i}º lugar: **{dep}** — {score} pontos")

        # Mostrar gráfico de barras dos top 5
        top5 = ranking[:5]
        nomes = [x[0] for x in top5]
        scores = [x[1] for x in top5]
        df_graf = pd.DataFrame({"Deputado": nomes, "Afinidade": scores})
        st.bar_chart(df_graf.set_index("Deputado"))

        # Mostrar deputado com menor afinidade
        dep_menor = ranking[-1][0]
        score_menor = ranking[-1][1]
        st.subheader(f"😕 Deputado com menor afinidade: {dep_menor} — {score_menor} pontos")

        # Mostrar dados do campeão
        dep_vencedor = ranking[0][0]
        nome_vencedor = dep_vencedor.split(" (")[0]

        st.subheader(f"🧾 Quem é {nome_vencedor}?")
        resumo, imagem_url = buscar_wikipedia_info(nome_vencedor)
        if imagem_url:
            st.image(imagem_url, width=200)
        st.write(resumo)

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

