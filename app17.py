import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Dashboard de Despesas de TI")

def carregar_dados(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, header=1)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}")
        return None

    # Remover primeiras linhas que não são dados
    df = df.iloc[2:].reset_index(drop=True)

    # Colunas para remover se existirem
    col_remover = ['Unnamed: 0', 'Unnamed: 6', "Unnamed: 19", 'STATUS', 'CONTRATO', 'Contrato']
    df = df.drop(columns=[col for col in col_remover if col in df.columns], errors='ignore')

    # Tratar colunas 'dez/25' duplicadas
    dez_cols = [col for col in df.columns if col == 'dez/25']
    if len(dez_cols) > 1:
        idxs = [i for i, col in enumerate(df.columns) if col == 'dez/25']
        cols_to_drop = [df.columns[i] for i in idxs[1:]]
        df = df.drop(columns=cols_to_drop)

    # Renomear colunas dos meses
    nomes_meses = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25',
                   'jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'Total']
    inicio = 3
    for i, nome in enumerate(nomes_meses):
        pos = inicio + i
        if pos < len(df.columns):
            df.rename(columns={df.columns[pos]: nome}, inplace=True)

    # Filtrar linhas vazias em 'TIPO DE SERVIÇOS'
    if 'TIPO DE SERVIÇOS' in df.columns:
        df = df[df['TIPO DE SERVIÇOS'].notna() & (df['TIPO DE SERVIÇOS'].astype(str).str.strip() != "")]

    return df

def aplicar_filtros(df):
    if 'FORNECEDOR' not in df.columns:
        st.warning("Coluna 'FORNECEDOR' não encontrada no arquivo.")
        return df

    fornecedores = df['FORNECEDOR'].dropna().unique().tolist()
    fornecedores_excluir = st.multiselect("Selecione fornecedores para excluir:", fornecedores)
    if fornecedores_excluir:
        df = df[~df['FORNECEDOR'].isin(fornecedores_excluir)]
    return df

def formatar_valor(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_graficos(df):
    meses_colunas = ['jan/25', 'fev/25', 'mar/25', 'abr/25', 'mai/25', 'jun/25',
                     'jul/25', 'ago/25', 'set/25', 'out/25', 'nov/25', 'dez/25', 'Total']

    # Converter colunas para numérico
    for col in meses_colunas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    st.subheader("Dados filtrados")
    st.dataframe(df, height=600, width=1200)

    tab1, tab2, tab3, tab4 = st.tabs(["Despesa por Fornecedor", "Despesa por Mês", "Participação %", "Evolução Mensal"])

    with tab1:
        st.markdown("### Despesa total por fornecedor (R$)")
        if 'FORNECEDOR' in df.columns and 'Total' in df.columns:
            fornecedor_total = df.groupby('FORNECEDOR')['Total'].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(fornecedor_total, x='FORNECEDOR', y='Total',
                         text=fornecedor_total['Total'].apply(formatar_valor),
                         labels={'Total': 'Total (R$)'})
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para este gráfico.")

    with tab2:
        st.markdown("### Despesa total por mês")
        meses_existentes = [m for m in meses_colunas[:-1] if m in df.columns]
        if meses_existentes:
            df_mes = df[meses_existentes].sum().reset_index()
            df_mes.columns = ['Mês', 'Total']
            df_mes['Mês'] = pd.Categorical(df_mes['Mês'], categories=meses_existentes, ordered=True)
            df_mes = df_mes.sort_values('Mês')

            fig = px.bar(df_mes, x='Mês', y='Total',
                         text=df_mes['Total'].apply(formatar_valor),
                         labels={'Total': 'Total (R$)'})
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há colunas de meses para exibir.")

    with tab3:
        st.markdown("### Participação percentual das despesas por fornecedor")
        if 'FORNECEDOR' in df.columns and 'Total' in df.columns:
            fornecedor_total = df.groupby('FORNECEDOR')['Total'].sum().reset_index()
            total_geral = fornecedor_total['Total'].sum()
            fornecedor_total['%'] = (fornecedor_total['Total'] / total_geral) * 100
            fornecedor_total = fornecedor_total.sort_values('%', ascending=False)

            fig = px.bar(fornecedor_total, x='FORNECEDOR', y='%',
                         text=fornecedor_total['%'].apply(lambda x: f"{x:.1f}%"),
                         labels={'%': 'Percentual'})
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para este gráfico.")

    with tab4:
        st.markdown("### Evolução mensal por fornecedor e total")
        meses_disponiveis = [m for m in meses_colunas[:-1] if m in df.columns]
        meses_selecionados = st.multiselect("Selecione os meses para visualizar:", meses_disponiveis, default=meses_disponiveis)

        if meses_selecionados:
            df_periodo = df[['FORNECEDOR'] + meses_selecionados].copy()

            # Evolução por fornecedor
            df_fornecedor = df_periodo.groupby('FORNECEDOR')[meses_selecionados].sum().reset_index()
            df_melt = df_fornecedor.melt(id_vars='FORNECEDOR', var_name='Mês', value_name='Despesa')
            df_melt['Mês'] = pd.Categorical(df_melt['Mês'], categories=meses_selecionados, ordered=True)
            df_melt = df_melt.sort_values(['FORNECEDOR', 'Mês'])

            fig1 = px.line(df_melt, x='Mês', y='Despesa', color='FORNECEDOR', markers=True,
                           labels={'Despesa': 'Despesa (R$)', 'Mês': 'Mês'},
                           text=df_melt['Despesa'].apply(formatar_valor))
            fig1.update_traces(textposition='top center')
            st.plotly_chart(fig1, use_container_width=True)

            # Evolução total mensal
            df_total_mes = df_periodo[meses_selecionados].sum().reset_index()
            df_total_mes.columns = ['Mês', 'Despesa']
            df_total_mes['Mês'] = pd.Categorical(df_total_mes['Mês'], categories=meses_selecionados, ordered=True)
            df_total_mes = df_total_mes.sort_values('Mês')

            fig2 = px.line(df_total_mes, x='Mês', y='Despesa', markers=True,
                           labels={'Despesa': 'Despesa (R$)', 'Mês': 'Mês'},
                           text=df_total_mes['Despesa'].apply(formatar_valor))
            fig2.update_traces(textposition='top center')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Selecione pelo menos um mês para visualizar a evolução.")

uploaded_file = st.file_uploader("Faça upload do arquivo Excel", type=["xlsx"])
if uploaded_file:
    df = carregar_dados(uploaded_file)
    if df is not None:
        df_filtrado = aplicar_filtros(df)
        gerar_graficos(df_filtrado)
else:
    st.info("Aguardando upload do arquivo Excel.")
