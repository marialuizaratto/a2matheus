pip install wikipedia

import streamlit as st
import pandas as pd
import wikipedia

import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Afinidade Legislativa", layout="centered")

st.title("📊 Afinidade Legislativa com Deputados Federais")
st.write("""
Este aplicativo compara suas opiniões com votações reais da Câmara dos Deputados. 
Este aplicativo compara suas opiniões com votações reais da Câmara dos Deputados.

A partir das suas respostas, identificamos quais deputados do seu estado votam de forma mais alinhada com você.
""")

@@ -22,16 +21,9 @@ def carregar_dados():

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
}


ufs_disponiveis = sorted(df["uf"].dropna().unique())
@@ -55,12 +47,24 @@ def carregar_dados():


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

if st.button("Ver afinidade com deputados do seu estado"):
    st.subheader("🏆 Pódio de afinidade legislativa")
@@ -93,7 +97,6 @@ def buscar_wikipedia(nome):
        for i, (dep, score) in enumerate(ranking[:3], 1):
            st.write(f"{i}º lugar: {dep} — {score} pontos")

        # 1º lugar: mostrar descrição e como votou
        dep_vencedor = ranking[0][0]
        nome_vencedor = dep_vencedor.split(" (")[0]

@@ -105,8 +108,8 @@ def buscar_wikipedia(nome):
        votos_vencedor = df[(df["nome"] == nome_vencedor) & (df["uf"] == uf_usuario)]

        for id_vot, pergunta in perguntas.items():
            voto = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]["voto"].values
            voto_final = voto[0] if len(voto) > 0 else "Sem registro"
            voto_linha = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]
            voto_final = voto_linha["voto"].iloc[0] if not voto_linha.empty else "Sem registro"
            st.markdown(f"- **{pergunta}** → {voto_final}")
    else:
        st.info("Nenhum deputado encontrado para esse estado.")
