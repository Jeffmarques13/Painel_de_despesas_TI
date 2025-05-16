import pandas as pd
import streamlit as st

st.title("Dashboard de Despesas de TI")

uploaded_file = st.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Ler o arquivo Excel pulando a primeira linha e usando a segunda como cabeçalho
        df = pd.read_excel(uploaded_file, header=1, skiprows=[2])

        # Excluir colunas específicas que não interessam
        colunas_para_excluir = ['Coluna_0', 'STATUS', 'Coluna_06', 'Coluna_19']
        colunas_existentes = [col for col in colunas_para_excluir if col in df.columns]
        df = df.drop(columns=colunas_existentes)

        st.write("Prévia dos dados carregados:")
        st.dataframe(df.head())

        # Exibir as colunas detectadas para verificar nomes
        st.write("Colunas detectadas:")
        st.write(df.columns.tolist())

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
