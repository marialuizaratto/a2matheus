
import streamlit as st
import pandas as pd
import wikipedia
import requests
from bs4 import BeautifulSoup

# Configurações da página
st.set_page_config(page_title="Afinidade Legislativa", layout="centered")

st.title("📊 Afinidade Legislativa com Deputados Federais")
st.write("""
Este aplicativo compara suas opiniões com votações reais da Câmara dos Deputados.

A partir das suas respostas, identificamos quais deputados do seu estado votam de forma mais alinhada com você.
""")

# Função para carregar os dados dos deputados (você precisa ter o arquivo .csv ou similar)
@st.cache_data
def carregar_dados():
    return pd.read_csv("votacoes.csv")  # Substitua pelo caminho correto do seu CSV

df = carregar_dados()

# Perguntas associadas a cada id de votação
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
    "2310025-56": "Você apoia a Lei Aldir Blanc de incentivo à cultura?",
    "2453934-65": "Você concorda com o PL das fake news?",
    "2236291-85": "Você apoia o novo arcabouço fiscal (substituição do teto de gastos)?"
    # Adicione mais PLs conforme o seu CSV
}

ufs_disponiveis = sorted(df["uf"].dropna().unique())

# Seleção do estado
uf_usuario = st.selectbox("📍 Selecione seu estado:", ufs_disponiveis)

# Coleta das respostas do usuário
respostas_usuario = {}
st.subheader("🗳️ Suas opiniões")
for id_vot, pergunta in perguntas.items():
    resposta = st.radio(pergunta, ["Sim", "Não", "Não sei"], key=id_vot)
    respostas_usuario[id_vot] = resposta

# Função para buscar descrição do deputado na Wikipedia
def buscar_wikipedia(nome):
    wikipedia.set_lang("pt")
    url = f"https://pt.wikipedia.org/wiki/{nome.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        return wikipedia.summary(nome, sentences=3)
    except Exception:
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

# Botão de cálculo de afinidade
if st.button("Ver afinidade com deputados do seu estado"):
    st.subheader("🏆 Pódio de afinidade legislativa")

    deputados_uf = df[df["uf"] == uf_usuario]["nome"].unique()

    ranking = []

    for deputado in deputados_uf:
        votos_dep = df[(df["nome"] == deputado) & (df["id_votacao"].isin(perguntas.keys()))]
        score = 0

        for _, row in votos_dep.iterrows():
            id_vot = row["id_votacao"]
            voto_dep = row["voto"]
            voto_user = respostas_usuario.get(id_vot)

            if voto_user == "Não sei":
                continue
            elif (voto_user == "Sim" and voto_dep == "Sim") or (voto_user == "Não" and voto_dep == "Não"):
                score += 1

        ranking.append((deputado, score))

    ranking.sort(key=lambda x: x[1], reverse=True)

    if ranking:
        for i, (dep, score) in enumerate(ranking[:3], 1):
            st.write(f"{i}º lugar: {dep} — {score} pontos")

        # Mostra detalhes do 1º lugar
        dep_vencedor = ranking[0][0]
        nome_vencedor = dep_vencedor.split(" (")[0]

        st.subheader(f"🏅 {nome_vencedor}")
        st.markdown(f"📝 {buscar_wikipedia(nome_vencedor)}")

        votos_vencedor = df[(df["nome"] == nome_vencedor) & (df["uf"] == uf_usuario)]

        for id_vot, pergunta in perguntas.items():
            voto_linha = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]
            voto_final = voto_linha["voto"].iloc[0] if not voto_linha.empty else "Sem registro"
            st.markdown(f"- **{pergunta}** → {voto_final}")
    else:
        st.info("Nenhum deputado encontrado para esse estado.")
