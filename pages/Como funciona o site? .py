import streamlit as st

st.set_page_config(page_title="Como o Quiz Funciona", layout="centered")

st.title("📚 Entenda Como o Quiz Funciona")

st.markdown("""
Este quiz calcula a sua afinidade com deputados federais **com base em como eles votaram em temas importantes**.  
Ele compara suas opiniões pessoais com os votos reais dos deputados em plenário, mostrando quais parlamentares têm posições mais próximas das suas.

---

## 🧮 Como o algoritmo calcula a afinidade?

Para cada tema, você escolhe uma opinião numa escala de concordância:

- **Concordo muito** → peso **+2**  
- **Concordo** → peso **+1**  
- **Neutro/Não sei** → peso **0**  
- **Discordo** → peso **-1**  
- **Discordo muito** → peso **-2**

Os votos dos deputados são convertidos assim:

- **Voto "Sim"** → peso **+1**  
- **Voto "Não"** → peso **-1**  
- **Outros votos** (Abstenção, Obstrução, Ausente) → peso **0**

---

### 🧠 Cálculo da Pontuação — Exemplo Prático

Imagine que você respondeu:

- Pergunta A: **Concordo muito** (+2)  
- Pergunta B: **Discordo** (-1)  
- Pergunta C: **Neutro** (0)  

E o deputado votou:

- Pergunta A: **Sim** (+1)  
- Pergunta B: **Não** (-1)  
- Pergunta C: **Abstenção** (0)  

O cálculo seria:

- Pergunta A: 2 (sua opinião) × 1 (voto do deputado) = +2  
- Pergunta B: (-1) × (-1) = +1 (vocês concordam em discordar)  
- Pergunta C: 0 × 0 = 0  

**Pontuação final = 2 + 1 + 0 = +3**, indicando alta afinidade.

Quanto mais positiva a pontuação, mais próximo o deputado está das suas opiniões.

---

## 🟢 Legenda dos Votos

Na página de resultados, você verá como cada deputado votou em cada tema, com cores para facilitar a visualização:

- 🟢 **Verde** → Você e o deputado pensam parecido no tema.  
- 🔴 **Vermelho** → Vocês têm opiniões contrárias nesse tema.  
- ⚪️ **Cinza** → Pelo menos um lado ficou neutro ou não votou.

---

## 📌 Observações Importantes

- A pontuação considera apenas deputados do seu estado, para facilitar o contato e participação local.  
- Os dados são públicos e vêm das votações oficiais da Câmara dos Deputados.  
- Votos de abstenção, obstrução ou ausência **não influenciam** no cálculo, pois indicam falta de posicionamento.

---

## 🤔 Por que esse app é importante?

Você sabe como o deputado ou deputada em quem votou realmente vota nos projetos de lei?  
Muitas vezes, as decisões sobre temas que impactam diretamente a sua vida acontecem sem que a gente acompanhe ou entenda claramente o posicionamento dos nossos representantes.

Além disso, em muitas eleições, escolher o candidato ideal fica para a última hora, sem tempo de analisar o histórico real de votos.

Esse app te ajuda a:

- Conhecer quais deputados têm mais afinidade com suas opiniões políticas.  
- Tomar decisões eleitorais mais informadas, exercendo melhor a sua cidadania.  
- Acompanhar a atuação dos parlamentares no dia a dia, mesmo fora do período eleitoral.

---

## 📢 Transparência e Democracia

Todos os dados usados aqui são públicos, disponibilizados pela Câmara dos Deputados.  
Ao democratizar o acesso à informação, fortalecemos a democracia e incentivamos a participação consciente.

Use este app para se informar, compartilhar conhecimento e cobrar seus representantes!

---

""")

