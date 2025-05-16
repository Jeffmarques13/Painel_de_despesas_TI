import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Controle de Despesas", layout="wide")
st.title("📊 Controle de Despesas de TI")

arquivo = st.file_uploader("📁 Envie sua planilha Excel", type=["xlsx"])

if arquivo:
    # Lê o arquivo pulando as 3 primeiras linhas (até o cabeçalho real)
    df = pd.read_excel(arquivo, header=3)

    # Renomeia as colunas para facilitar o uso
    df.columns = ['Tipo de Serviço', 'Descrição', 'Vence', 'Fornecedor', 'Status']

    # Trata a coluna "Vence"
    df['Vence'] = pd.to_numeric(df['Vence'], errors='coerce')

    # Cria nova coluna com a data de vencimento convertida
    hoje = datetime.now()
    df['Data Vencimento'] = df['Vence'].apply(
        lambda dia: datetime(hoje.year, hoje.month, int(dia)) if not pd.isna(dia) and 1 <= dia <= 31 else pd.NaT
    )

    # Ajusta para o mês seguinte se a data já passou
    df['Data Vencimento'] = df['Data Vencimento'].apply(
        lambda d: d + pd.DateOffset(months=1) if pd.notna(d) and d < hoje else d
    )

    # Define cor da linha conforme vencimento e status
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
