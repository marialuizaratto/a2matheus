import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Afinidade Legislativa", layout="centered")

st.title("📊 Afinidade Legislativa com Deputados Federais")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("votos_camara.csv")
    return df

df = carregar_dados()

perguntas = {
    # ... seu dicionário de perguntas ...
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

@st.cache_data(show_spinner=False)
def buscar_info_deputado(id_dep):
    url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_dep}"
    resp = requests.get(url)
    if resp.status_code == 200:
        dados = resp.json()["dados"]
        return {
            "nome": dados["nome"],
            "partido": dados["ultimoStatus"]["siglaPartido"],
            "uf": dados["ultimoStatus"]["siglaUf"],
            "foto": dados["ultimoStatus"]["urlFoto"]
        }
    return None

if st.button("Ver afinidade com deputados do seu estado"):
    pontuacoes = {}

    for id_vot, resp_user in respostas_usuario.items():
        peso_user = pesos_usuario.get(resp_user, 0)
        votos = df[(df["id_votacao"] == id_vot) & (df["uf"] == uf_usuario)]

        for _, linha in votos.iterrows():
            id_dep = linha["id_dep"]
            voto_dep = linha["voto"]

            if voto_dep == "Sim":
                peso_dep = 1
            elif voto_dep == "Não":
                peso_dep = -1
            else:
                peso_dep = 0

            compat = peso_user * peso_dep

            if id_dep is not None:
                pontuacoes[id_dep] = pontuacoes.get(id_dep, 0) + compat

    if not pontuacoes:
        st.info("Nenhum deputado encontrado para esse estado.")
    else:
        ranking = sorted(pontuacoes.items(), key=lambda x: x[1], reverse=True)
        st.write("### Top 3 deputados mais alinhados:")
        for i, (id_dep, score) in enumerate(ranking[:3], 1):
            info = buscar_info_deputado(id_dep)
            if info:
                st.write(f"{i}º lugar: {info['nome']} ({info['partido']}-{info['uf']}) — {score} pontos")
                st.image(info["foto"], width=120)
            else:
                st.write(f"{i}º lugar: Deputado ID {id_dep} — {score} pontos (Info não disponível)")

        # Detalhes do campeão
        id_vencedor = ranking[0][0]
        info_vencedor = buscar_info_deputado(id_vencedor)
        if info_vencedor:
            st.subheader(f"🧾 Quem é {info_vencedor['nome']}?")
            st.image(info_vencedor["foto"], width=200)
            st.write(f"Partido: {info_vencedor['partido']} - {info_vencedor['uf']}")

            st.subheader(f"📌 Como {info_vencedor['nome']} votou nas questões:")

            votos_vencedor = df[(df["id_dep"] == id_vencedor) & (df["uf"] == uf_usuario)]

            for id_vot, pergunta in perguntas.items():
                voto_linha = votos_vencedor[votos_vencedor["id_votacao"] == id_vot]
                voto_final = voto_linha["voto"].iloc[0] if not voto_linha.empty else "Sem registro"

                peso_user = pesos_usuario[respostas_usuario[id_vot]]
                if voto_final == "Sim":
                    peso_dep = 1
                elif voto_final == "Não":
                    peso_dep = -1
                else:
                    peso_dep = 0

                if peso_user == 0 or peso_dep == 0:
                    cor = "gray"
                elif peso_user == peso_dep or peso_user * peso_dep > 0:
                    cor = "green"
                else:
                    cor = "red"

                st.markdown(
                    f'<span style="color:{cor}">• <b>{pergunta}</b> → {voto_final}</span>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Não foi possível recuperar informações do deputado vencedor.")

