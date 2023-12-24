import pandas as pd
import streamlit as st
from datetime import timedelta
import plotly.express as px

def carregar_faturas():
    st.sidebar.header("Faturas")

    # Widget de upload de arquivo
    faturas_credito = st.sidebar.file_uploader("Escolha um arquivo CSV", type="csv", accept_multiple_files=True, key='faturas')

    if faturas_credito is not None:
        df = pd.DataFrame()
        for fatura in faturas_credito:
            df_temp = pd.read_csv(fatura)
            if 'Unnamed: 0' in df_temp.columns:
                df_temp = df_temp.drop(columns=['Unnamed: 0'])   
 
            df = pd.concat([df, df_temp], axis=0).drop_duplicates()
        
        # Renomeando as colunas 
        df.columns = ['Data', 'Categoria', 'Loja', 'Valor (R$)']
        # Remover o pagamento da fatura
        df = df[df['Categoria'] != 'payment']
        # Converter em datetime
        df['Data'] = pd.to_datetime(df['Data'])

        st.sidebar.header('Outras compras')
        option = st.sidebar.selectbox('Você deseja adicionar outras compras?',('Sim', 'Não'))
        if option == "Sim":
            # Widget de upload de arquivo
            outras_compras = st.sidebar.file_uploader("Escolha um arquivo EXCEL", type="xlsx", key = 'outras_compras')

            df_outras = pd.read_excel(outras_compras)
            # Converter em datetime
            df_outras['Data'] = pd.to_datetime(df_outras['Data'])

            df = pd.concat([df, df_outras]).drop_duplicates()
    return df


def intervalos(df):
    """
    Filtra um DataFrame de despesas em três intervalos de tempo: últimos 30 dias,
    dias entre 30 e 60 dias atrás, e últimos 365 dias.

    Parâmetros:
    - df (DataFrame): O DataFrame contendo informações de despesas com a coluna 'Data'.

    Retorna:
    - df_30_dias (DataFrame): DataFrame filtrado para os últimos 30 dias.
    - df_30d_60d (DataFrame): DataFrame filtrado para os dias entre 30 e 60 dias atrás.
    - df_365_dias (DataFrame): DataFrame filtrado para os últimos 365 dias.
    """
    # Calcular o gasto nos últimos 30 dias a partir da data máxima
    data_maxima = df['Data'].max()
    data_30_dias_atras = data_maxima - timedelta(days=30)
    data_60_dias_atras = data_maxima - timedelta(days=60)
    data_365_dias_atras = data_maxima - timedelta(days=365)

    # Filtrar o DataFrame para os últimos 30 dias
    df_30_dias = df[df['Data'] > data_30_dias_atras]

    # Filtrar o DataFrame para os dias entre 30 e 60 dias atrás
    df_30d_60d  = df[(df['Data'] > data_60_dias_atras) & (df['Data'] < data_30_dias_atras)]

    # Filtrar o DataFrame para os últimos 365 dias
    df_365_dias = df[df['Data'] > data_365_dias_atras]

    return df_30_dias, df_30d_60d, df_365_dias

def indicadores(df_30_dias, df_30d_60d):
    """
    Calcula e exibe indicadores relacionados aos gastos nos últimos 30 dias e entre 30 e 60 dias atrás.

    Parâmetros:
    - df_30_dias (DataFrame): DataFrame contendo informações de despesas nos últimos 30 dias.
    - df_30d_60d (DataFrame): DataFrame contendo informações de despesas entre 30 e 60 dias atrás.
    """
    # Calcular o gasto nos últimos 30 dias
    gasto_30d = df_30_dias['Valor (R$)'].sum()
    
    # Categoria de maior gasto nos últimos 30 dias
    categoria_gastona = df_30_dias.groupby('Categoria')['Valor (R$)'].sum().sort_values(ascending=False).index[0]

    # Calcular o gasto entre 30 e 60 dias atrás
    gasto_30d_60d = df_30d_60d['Valor (R$)'].sum()

    # Exibir os indicadores usando Streamlit
    st.header('Indicadores')
    col1, col2 = st.columns([1, 2])
    col1.metric(label="Gasto dos últimos 30 dias", value=gasto_30d, delta=gasto_30d - gasto_30d_60d, delta_color='inverse')
    col2.text('Categoria com maior gasto nos últimos 30 dias')

    col2.markdown(f'<p style="color: red;">{categoria_gastona}</p>', unsafe_allow_html=True)

def grafico_linhas(df_365_dias):
    """
    Cria e exibe um gráfico de linhas com gastos acumulados nos últimos 365 dias.

    Parâmetros:
    - df_365_dias (DataFrame): DataFrame contendo informações de despesas nos últimos 365 dias.
    """
    st.header('Gastos acumulados')

    # Agrupar por data e calcular gastos acumulados
    df_dia = df_365_dias.groupby(['Data'])['Valor (R$)'].sum().reset_index()
    df_dia['Valor (R$)'] = df_dia['Valor (R$)'].cumsum()

    # Criar o gráfico de linhas
    fig = px.line(df_dia, y='Valor (R$)', x='Data', title="Gastos Acumulados nos últimos 365 dias")

    # Configurar a posição horizontal do título
    fig.update_layout(title=dict(x=0.0, font=dict(color='blue')))

    # Exibir o gráfico usando Streamlit
    st.plotly_chart(fig)

def grafico_categorias(df_30_dias, df_365_dias):
    """
    Cria e exibe gráficos de gastos por categoria nos últimos 365 dias e nos últimos 30 dias.

    Parâmetros:
    - df_30_dias (DataFrame): DataFrame contendo informações de despesas nos últimos 30 dias.
    - df_365_dias (DataFrame): DataFrame contendo informações de despesas nos últimos 365 dias.
    """
    st.header('Gastos por Categoria')

    # Configurar a disposição das colunas no Streamlit
    col1, col2 = st.columns([2, 1])

    # Preparar DataFrame para o gráfico de barras empilhadas
    df_barras_mes = df_365_dias.copy()
    df_barras_mes['Mês'] = df_barras_mes['Data'].dt.month.astype('str') + '-' + df_barras_mes['Data'].dt.year.astype('str')
    df_barras_mes['Ano'] = df_barras_mes['Data'].dt.year
    df_barras_mes['mes_ordem'] = df_barras_mes['Data'].dt.month

    df_barras_mes = df_barras_mes.groupby(['Ano', 'mes_ordem', 'Mês', 'Categoria'])['Valor (R$)'].sum().reset_index()

    df_barras_mes = df_barras_mes.sort_values(by=['Ano', 'mes_ordem', 'Valor (R$)'])
    ordem_meses = df_barras_mes[['Mês']].drop_duplicates()['Mês']

    # Criar o gráfico de barras empilhadas
    fig_barras = px.bar(df_barras_mes, x='Mês', y='Valor (R$)', color='Categoria',
                        title='Gastos nos últimos 365 dias',
                        labels={'Mês': 'Mês', 'Valor (R$)': 'Gastos'},
                        category_orders={'Mês': ordem_meses}, height=400, width=400)
    
    # Configurar a posição horizontal do título
    fig_barras.update_layout(title=dict(x=0.0, font=dict(color='blue')))

    # Adicionar o gráfico de barras ao Streamlit
    col1.plotly_chart(fig_barras)

    # Criar o gráfico de pizza
    fig_pizza = px.pie(df_30_dias, values='Valor (R$)', names='Categoria',
                       title='Gastos nos últimos 30 dias', width=300, height=500)
    
    # Configurar a posição horizontal do título
    fig_pizza.update_layout(title=dict(x=0.0, font=dict(color='blue')))

    # Adicionar o gráfico de pizza ao Streamlit
    col2.plotly_chart(fig_pizza)

def faturas(df):
    """
    Exibe as faturas em um DataFrame ordenado por data de forma decrescente e remove linhas duplicadas.

    Parâmetros:
    - df (DataFrame): DataFrame contendo informações de faturas.

    Retorna:
    - None
    """
    st.header('Faturas')

    # Ordenar o DataFrame por data de forma decrescente
    df = df.sort_values(by='Data', ascending=False).reset_index(drop=True)

    # Remover linhas duplicadas
    df = df.drop_duplicates()

    # Exibir o DataFrame usando Streamlit
    st.dataframe(df)