import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Controle de Despesas", layout="wide")
st.title("📊 Controle de Despesas de TI")

arquivo = st.file_uploader("📁 Envie sua planilha Excel", type=["xlsx"])

if arquivo:
    # Lê o arquivo a partir da 3ª linha útil (linha 4, índice 3)
    df_original = pd.read_excel(arquivo, header=3)

    # Seleciona apenas as 5 primeiras colunas úteis
    df = df_original.iloc[:, :5]
    df.columns = ['Tipo de Serviço', 'Descrição', 'Vence', 'Fornecedor', 'Status']

    # Converte a coluna 'Vence' para número
    df['Vence'] = pd.to_numeric(df['Vence'], errors='coerce')

    # Cria coluna com data de vencimento
    hoje = datetime.now()
    df['Data Vencimento'] = df['Vence'].apply(
        lambda dia: datetime(hoje.year, hoje.month, int(dia)) if not pd.isna(dia) and 1 <= dia <= 31 else pd.NaT
    )

    # Ajusta para mês seguinte, se data já passou
    df['Data Vencimento'] = df['Data Vencimento'].apply(
        lambda d: d + pd.DateOffset(months=1) if pd.notna(d) and d < hoje else d
    )

    # Define cores
    def cor_linha(row):
        if row['Status'] and 'em dia' in str(row['Status']).lower():
            return 'background-color: #d4edda;'  # Verde claro
        elif pd.isna(row['Data Vencimento']):
            return ''
        elif row['Data Vencimento'] < hoje:
            return 'background-color: #f8d7da;'  # Vermelho claro
        elif (row['Data Vencimento'] - hoje).days <= 5:
            return 'background-color: #fff3cd;'  # Amarelo claro
        else:
            return ''

    st.subheader("📅 Despesas com Vencimentos")
    st.dataframe(df.style.apply(lambda x: [cor_linha(x)], axis=1), use_container_width=True)
