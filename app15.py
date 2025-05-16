import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

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

        # Excluir colunas STATUS e CONTRATO sem mexer no restante do código
        for col in ['STATUS', 'Contrato']:
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
        col_inicio = 3
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

        # Sem filtro para 'TIPO DE SERVIÇOS' (removido conforme solicitado)
        df_filtrado = df.copy()

        # Converter colunas de valores para numérico
        meses_colunas = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25',
                         'jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'Total']
        for col in meses_colunas:
            if col in df_filtrado.columns:
                df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')

        # Prévia da tabela com filtro aplicado e maior altura e largura
        st.subheader("Prévia dos dados após correções e filtro")
        st.dataframe(df_filtrado, height=900, width=1400)

        # Gráfico 1 – Despesa total por fornecedor (em R$)
        st.subheader("Despesa total por fornecedor (R$)")
        if 'FORNECEDOR' in df_filtrado.columns and 'Total' in df_filtrado.columns:
            fornecedor_total = df_filtrado.groupby('FORNECEDOR')['Total'].sum().sort_values(ascending=False).reset_index()
            fig1 = px.bar(fornecedor_total, x='FORNECEDOR', y='Total',
                          text=fornecedor_total['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                          labels={'Total': 'Total (R$)'})
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2 – Despesa total por mês
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

        # Gráfico 3 – Participação percentual das despesas por fornecedor (Total Anual)
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

        # Filtro por período (meses)
        st.subheader("Filtro por período")
        meses_disponiveis = [m for m in meses_colunas[:-1] if m in df_filtrado.columns]
        meses_selecionados = st.multiselect("Selecione o(s) mês(es) para visualizar:", meses_disponiveis, default=meses_disponiveis)

        if meses_selecionados:
            df_periodo = df_filtrado[['FORNECEDOR'] + meses_selecionados].copy()

            # Gráfico 4 – Evolução mensal por fornecedor com valores nos pontos
            st.subheader("Evolução mensal por fornecedor")
            df_fornecedor = df_periodo.groupby('FORNECEDOR')[meses_selecionados].sum().reset_index()
            df_melt_fornecedor = df_fornecedor.melt(id_vars='FORNECEDOR', var_name='Mês', value_name='Despesa')

            df_melt_fornecedor['Mês'] = pd.Categorical(df_melt_fornecedor['Mês'], categories=meses_selecionados, ordered=True)
            df_melt_fornecedor = df_melt_fornecedor.sort_values(['FORNECEDOR', 'Mês'])

            fig4 = px.line(df_melt_fornecedor, x='Mês', y='Despesa', color='FORNECEDOR', markers=True,
                           labels={'Despesa': 'Despesa (R$)', 'Mês': 'Mês'})
            # Remover texto para evitar sobreposição
            fig4.update_traces(text=None)
            fig4.update_layout(margin=dict(t=50, b=100))
            st.plotly_chart(fig4, use_container_width=True)

            # Gráfico 5 – Evolução total por mês com valores nos pontos
            st.subheader("Evolução total por mês")
            df_evol_total = df_periodo[meses_selecionados].sum().reset_index()
            df_evol_total.columns = ['Mês', 'Despesa']
            df_evol_total['Mês'] = pd.Categorical(df_evol_total['Mês'], categories=meses_selecionados, ordered=True)
            df_evol_total = df_evol_total.sort_values('Mês')

            fig5 = px.line(df_evol_total, x='Mês', y='Despesa', markers=True,
                           labels={'Despesa': 'Despesa (R$)', 'Mês': 'Mês'})
            fig5.update_traces(text=df_evol_total['Despesa'].apply(lambda x: f"R$ {x:,.2f}"), textposition='top center')
            st.plotly_chart(fig5, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
