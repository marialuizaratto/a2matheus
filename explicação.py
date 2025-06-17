import streamlit as st

st.set_page_config(page_title="Como o Quiz Funciona", layout="centered")

st.title("📚 Entenda Como o Quiz Funciona")

st.markdown("""
Este quiz calcula a sua afinidade com deputados federais **com base em como eles votaram em temas importantes**.

Ele compara suas opiniões com os votos reais dos deputados em plenário.

---

## 🧮 Como o algoritmo calcula a afinidade?

Para cada tema, você escolhe uma opinião usando a escala:

- **Concordo muito** → peso **+2**
- **Concordo** → peso **+1**
- **Neutro/Não sei** → peso **0**
- **Discordo** → peso **-1**
- **Discordo muito** → peso **-2**

Os votos dos deputados são transformados assim:

- **Voto "Sim"** → peso **+1**
- **Voto "Não"** → peso **-1**
- **Outros votos** (Abstenção, Obstrução, Ausente) → peso **0**

---

### 🧠 Cálculo da Pontuação

Para cada tema:
- Multiplicamos o **seu peso** pela **posição do deputado**.
- Somamos esses valores para todos os temas.

**Quanto mais positiva a pontuação, maior a afinidade entre você e o deputado.**

---

## 🟢 Legenda dos Votos

Na página de resultado, os votos são mostrados com cores para indicar alinhamento:

- 🟢 **Verde** → Você e o deputado pensam parecido no tema.
- 🔴 **Vermelho** → Vocês discordam nesse tema.
- ⚪️ **Cinza** → Pelo menos um dos lados ficou neutro ou ausente.

---

### 📌 Observações

- A pontuação considera apenas deputados do seu estado.
- Os dados vêm de votações públicas da Câmara dos Deputados.
- Votos de abstenção, obstrução ou ausência **não influenciam** o resultado final.

---
""")
