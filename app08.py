import pandas as pd
import streamlit as st

st.title("Dashboard de Despesas de TI")

uploaded_file = st.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        # Ler Excel com cabeçalho na linha 2 (index 1)
        df = pd.read_excel(uploaded_file, header=1)

        # Remover as duas primeiras linhas (0 e 1)
        df = df.iloc[2:].reset_index(drop=True)
        
        # Excluir coluna 'Unnamed: 0' se existir
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])

        # Excluir coluna 'Unnamed: 6' se existir
        if 'Unnamed: 6' in df.columns:
            df = df.drop(columns=['Unnamed: 6'])

        # Excluir coluna 'Unnamed: 19' se existir
        if 'Unnamed: 19' in df.columns:
            df = df.drop(columns=['Unnamed: 19'])

        # Identificar colunas 'dez/25' duplicadas e excluir todas, exceto a primeira
        cols_dez = [col for col in df.columns if col == 'dez/25']
        if len(cols_dez) > 1:
            # Pega os índices das colunas 'dez/25'
            dez_cols_idx = [i for i, col in enumerate(df.columns) if col == 'dez/25']
            # Remove todas exceto a primeira
            cols_para_remover = [df.columns[i] for i in dez_cols_idx[1:]]
            df = df.drop(columns=cols_para_remover)

        # Renomear colunas de mês da posição 6 até 17 para os nomes corretos
        meses_correto = ['jan/25','fev/25','mar/25','abr/25','mai/25','jun/25',
                        'jul/25','ago/25','set/25','out/25','nov/25','dez/25' , 'Total']

        for i, mes in enumerate(meses_correto):
            idx_col = 5 + i
            if idx_col < len(df.columns):
                df.rename(columns={df.columns[idx_col]: mes}, inplace=True)

        st.subheader("Prévia dos dados após correções")
        st.dataframe(df.head())

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
