import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Dashboard de Despesas de TI")

uploaded_file = st.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=1)
        df = df.iloc[2:].reset_index(drop=True)

        # Excluir colunas desnecessárias
        for col in ['Unnamed: 0', 'Unnamed: 6', "Unnamed: 19"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Remover colunas 'dez/25' duplicadas (manter apenas a primeira)
        dez_cols = [col for col in df.columns if col == 'dez/25']
        if len(dez_cols) > 1:
            idxs = [i for i, col in enumerate(df.columns) if col == 'dez/25']
            cols_to_drop = [df.columns[i] for i in idxs[1:]]
            df = df.drop(columns=cols_to_drop)

        # Renomear colunas dos meses
        nomes_meses = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25',
                       'jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'Total']
        col_inicio = 5
        for i, nome_mes in enumerate(nomes_meses):
            pos = col_inicio + i
            if pos < len(df.columns):
                df.rename(columns={df.columns[pos]: nome_mes}, inplace=True)

        # Remover linhas com 'TIPO DE SERVIÇOS' vazias
        if 'TIPO DE SERVIÇOS' in df.columns:
            df = df[df['TIPO DE SERVIÇOS'].notna() & (df['TIPO DE SERVIÇOS'].astype(str).str.strip() != "")]

        # Filtro para excluir fornecedores
        if 'FORNECEDOR' in df.columns:
            fornecedores = df['FORNECEDOR'].dropna().unique().tolist()
            fornecedores_excluir = st.multiselect("Selecione os fornecedores que deseja excluir:", fornecedores)
            if fornecedores_excluir:
                df = df[~df['FORNECEDOR'].isin(fornecedores_excluir)]

        # --- Filtro interativo para TIPO DE SERVIÇOS ---
        tipos_servico = df['TIPO DE SERVIÇOS'].unique().tolist()
        selecionados = st.multiselect("Selecione o(s) tipo(s) de serviço para filtrar:", tipos_servico, default=tipos_servico)
        df_filtrado = df[df['TIPO DE SERVIÇOS'].isin(selecionados)]

        # Excluir coluna CONTRATO se existir
        if 'CONTRATO' in df_filtrado.columns:
            df_filtrado = df_filtrado.drop(columns=['CONTRATO'])

        # Converter colunas de valores para numérico
        meses_colunas = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25',
                         'jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'Total']
        for col in meses_colunas:
            if col in df_filtrado.columns:
                df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')

        # Prévia da tabela com filtro aplicado e maior altura
        st.subheader("Prévia dos dados após correções e filtro")
        st.dataframe(df_filtrado, height=600)

        # Gráfico 1 – Despesa total por fornecedor (em R$)
        st.subheader("Despesa total por fornecedor (R$)")
        if 'FORNECEDOR' in df_filtrado.columns and 'Total' in df_filtrado.columns:
            fornecedor_total = df_filtrado.groupby('FORNECEDOR')['Total'].sum().sort_values(ascending=False).reset_index()
            fig1 = px.bar(fornecedor_total, x='FORNECEDOR', y='Total',
                          text=fornecedor_total['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                          labels={'Total': 'Total (R$)'})
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2 – Despesa por mês
        st.subheader("Despesa total por mês")
        meses_existentes = [m for m in meses_colunas[:-1] if m in df_filtrado.columns]
        df_mes = df_filtrado[meses_existentes].sum().reset_index()
        df_mes.columns = ['Mês', 'Total']
        df_mes['Mês'] = pd.Categorical(df_mes['Mês'], categories=meses_colunas[:-1], ordered=True)
        df_mes = df_mes.sort_values('Mês')

        fig2 = px.bar(df_mes, x='Mês', y='Total',
                      text=df_mes['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                      labels={'Total': 'Total (R$)'})
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

        # Gráfico 3 – Participação percentual por fornecedor (Total Anual)
        st.subheader("Participação percentual das despesas por fornecedor")
        if 'FORNECEDOR' in df_filtrado.columns and 'Total' in df_filtrado.columns:
            fornecedor_total = df_filtrado.groupby('FORNECEDOR')['Total'].sum().reset_index()
            total_geral = fornecedor_total['Total'].sum()
            fornecedor_total['%'] = (fornecedor_total['Total'] / total_geral) * 100
            fig3 = px.bar(fornecedor_total.sort_values('%', ascending=False), x='FORNECEDOR', y='%',
                          text=fornecedor_total['%'].apply(lambda x: f"{x:.1f}%"),
                          labels={'%': 'Percentual'})
            fig3.update_traces(textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
