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

        # Limpeza inicial
        for col in ['Unnamed: 0', 'Unnamed: 6', "Unnamed: 19"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Remover colunas 'dez/25' duplicadas
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
        df = df[df['TIPO DE SERVIÇOS'].notna() & (df['TIPO DE SERVIÇOS'].astype(str).str.strip() != "")]

        # Filtro para excluir fornecedores
        fornecedores = df['FORNECEDOR'].dropna().unique().tolist()
        fornecedores_excluir = st.multiselect("Selecione os fornecedores que deseja excluir:", fornecedores)
        if fornecedores_excluir:
            df = df[~df['FORNECEDOR'].isin(fornecedores_excluir)]

        # Excluir coluna CONTRATO se existir
        if 'CONTRATO' in df.columns:
            df = df.drop(columns=['CONTRATO'])

        # Converter colunas de valores para numérico
        meses_colunas = nomes_meses[:-1]  # Todos menos 'Total'
        for col in meses_colunas + ['Total']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Mostrar tabela com altura aumentada para melhor visualização
        st.subheader("Prévia dos dados após correções")
        st.dataframe(df, height=600)

        # Gráfico 1 – Despesa total por fornecedor (em R$)
        st.subheader("Despesa total por fornecedor (R$)")
        if 'FORNECEDOR' in df.columns and 'Total' in df.columns:
            fornecedor_total = df.groupby('FORNECEDOR')['Total'].sum().sort_values(ascending=False).reset_index()
            fig1 = px.bar(fornecedor_total, x='FORNECEDOR', y='Total',
                          text=fornecedor_total['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                          labels={'Total': 'Total (R$)'})
            fig1.update_traces(textposition='outside')
            st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2 – Despesa por mês
        st.subheader("Despesa total por mês")
        meses_existentes = [m for m in meses_colunas if m in df.columns]
        df_mes = df[meses_existentes].sum().reset_index()
        df_mes.columns = ['Mês', 'Total']
        df_mes['Mês'] = pd.Categorical(df_mes['Mês'], categories=meses_colunas, ordered=True)
        df_mes = df_mes.sort_values('Mês')

        fig2 = px.bar(df_mes, x='Mês', y='Total',
                      text=df_mes['Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                      labels={'Total': 'Total (R$)'})
        fig2.update_traces(textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

        # Gráfico 3 – Participação percentual por fornecedor (Total Anual)
        st.subheader("Participação percentual das despesas por fornecedor")
        fornecedor_total_pct = df.groupby('FORNECEDOR')['Total'].sum().reset_index()
        total_geral = fornecedor_total_pct['Total'].sum()
        fornecedor_total_pct['%'] = (fornecedor_total_pct['Total'] / total_geral) * 100
        fig3 = px.bar(fornecedor_total_pct.sort_values('%', ascending=False), x='FORNECEDOR', y='%',
                      text=fornecedor_total_pct['%'].apply(lambda x: f"{x:.1f}%"),
                      labels={'%': 'Percentual'})
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

        # Novo: Gráfico interativo por Tipo de Serviço
        st.subheader("Despesa mensal por Tipo de Serviço")
        tipos_servicos = df['TIPO DE SERVIÇOS'].unique().tolist()
        tipo_selecionado = st.selectbox("Selecione o Tipo de Serviço:", tipos_servicos)

        df_filtrado = df[df['TIPO DE SERVIÇOS'] == tipo_selecionado]
        soma_por_mes = df_filtrado[meses_colunas].sum().reset_index()
        soma_por_mes.columns = ['Mês', 'Valor']
        soma_por_mes['Mês'] = pd.Categorical(soma_por_mes['Mês'], categories=meses_colunas, ordered=True)
        soma_por_mes = soma_por_mes.sort_values('Mês')

        fig4 = px.bar(soma_por_mes, x='Mês', y='Valor',
                      text=soma_por_mes['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                      labels={'Valor': 'Valor (R$)', 'Mês': 'Mês'},
                      title=f'Despesa mensal para o tipo de serviço: {tipo_selecionado}')
        fig4.update_traces(textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Por favor, faça upload do arquivo Excel para continuar.")
