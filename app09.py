import pandas as pd
import streamlit as st

st.title("Dashboard de Despesas de TI")

uploaded_file = st.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Ler Excel com cabeçalho na linha 2 (index 1)
        df = pd.read_excel(uploaded_file, header=1)

        # Remover as duas primeiras linhas visuais
        df = df.iloc[2:].reset_index(drop=True)

        # Excluir colunas desnecessárias
        for col in ['Unnamed: 0', 'Unnamed: 6' , 'Unnamed: 19']:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Remover colunas 'dez/25' duplicadas (manter apenas a primeira)
        dez_cols = [col for col in df.columns if col == 'dez/25']
        if len(dez_cols) > 1:
            idxs = [i for i, col in enumerate(df.columns) if col == 'dez/25']
            cols_to_drop = [df.columns[i] for i in idxs[1:]]
            df = df.drop(columns=cols_to_drop)

        # Renomear colunas de meses
        nomes_meses = ['jan/25','fev/25','mar/25','abr/25','mai/25','jun/25',
                       'jul/25','ago/25','set/25','out/25','nov/25','dez/25' , 'Valor Total']
        col_inicio = 5
        for i, nome_mes in enumerate(nomes_meses):
            pos = col_inicio + i
            if pos < len(df.columns):
                df.rename(columns={df.columns[pos]: nome_mes}, inplace=True)
        # Remover linhas onde 'TIPO DE SERVIÇOS' está vazio ou nulo
        if 'TIPO DE SERVIÇOS' in df.columns:
         df[df['TIPO DE SERVIÇOS'].notna() & (df['TIPO DE SERVIÇOS'].astype(str).str.strip() != "None")]

        # Seleção de fornecedores a excluir
        if 'FORNECEDOR' in df.columns:
            fornecedores = df['FORNECEDOR'].dropna().unique().tolist()
            fornecedores_excluir = st.multiselect("Selecione os fornecedores que deseja excluir:", fornecedores)

            if fornecedores_excluir:
                df = df[~df['FORNECEDOR'].isin(fornecedores_excluir)]

        st.subheader("Prévia dos dados após correções")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
