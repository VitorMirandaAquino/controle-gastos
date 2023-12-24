

import streamlit as st 



from dash_preprocessing import carregar_faturas, intervalos, indicadores, grafico_linhas, grafico_categorias, faturas

df = carregar_faturas()

if len(df) > 0:
    df_30_dias, df_30d_60d, df_365_dias = intervalos(df)
    st.title('Controle de Gastos')
    indicadores(df_30_dias, df_30d_60d)
    grafico_linhas(df_365_dias)
    grafico_categorias(df_30_dias, df_365_dias)
    faturas(df)