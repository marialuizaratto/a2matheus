if ranking:
    # Top 3 e o menos compatível
    top3 = ranking[:3]
    menos_compatível = ranking[-1]
    deputados_exibidos = sorted(top3 + [menos_compatível], key=lambda x: x[1])  # ordenado crescente

    st.subheader("📊 Afinidade (ordem crescente)")

    # DataFrame para gráfico
    df_graf = pd.DataFrame({
        "Deputado": [x[0] for x in deputados_exibidos],
        "Afinidade": [x[1] for x in deputados_exibidos]
    })

    # Estilo do gráfico manual com altair para customizar a cor
    import altair as alt

    grafico = alt.Chart(df_graf).mark_bar(color="#1f4e79").encode(
        x=alt.X("Afinidade:Q"),
        y=alt.Y("Deputado:N", sort="-x"),
        tooltip=["Deputado", "Afinidade"]
    ).properties(height=300)

    st.altair_chart(grafico, use_container_width=True)

    # Exibe afinidade em barra de progresso por deputado
    st.subheader("📈 Detalhamento visual da afinidade")

    for nome, score in deputados_exibidos:
        score_norm = (score + 20) / 40  # normaliza entre 0 e 1 assumindo pontuação de -20 a +20
        score_norm = max(0.0, min(1.0, score_norm))  # garante que está entre 0 e 1
        st.markdown(f"**{nome}** — {score} pontos")
        st.progress(score_norm)

