import streamlit as st
import pandas as pd

st.title("💼 Tratamento de Planilha de Despesas")

arquivo = st.file_uploader("📁 Envie sua planilha Excel", type=["xlsx"])

if arquivo:
    # Lê o arquivo sem considerar a primeira linha como cabeçalho
    df = pd.read_excel(arquivo, sheet_name=0, header=None)

    st.subheader("👀 Visualização das primeiras linhas da planilha (sem cabeçalho)")
    st.write(df.head(10))  # mostra as 10 primeiras linhas

    # Para a execução para você analisar o conteúdo
    st.stop()
