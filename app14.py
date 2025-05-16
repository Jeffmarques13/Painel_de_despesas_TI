import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Dashboard de Despesas de TI")

# Widget fora da função cacheada
uploaded_file = st.file_uploader("Importe o arquivo Excel com os dados de despesas", type=["xlsx"])

@st.cache_data(ttl=600)
def load_data(file):
    if file is None:
        return pd.DataFrame()

    try:
        df = pd.read_excel(file)
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()

        colunas_esperadas = ['Total (R$)', 'Mês', 'Tipo de Serviço', 'Fornecedor']
        for col in colunas_esperadas:
            if col not in df.columns:
                # Para não usar st.error aqui (fora da função cache), apenas retorna vazio
                return pd.DataFrame()

        df['Total (R$)'] = pd.to_numeric(df['Total (R$)'], errors='coerce')
        if df['Total (R$)'].isna().mean() > 0.2:
            # Mensagem de aviso fora da função cacheada depois
            pass

        df['Mês'] = df['Mês'].astype(str)
        return df

    except Exception:
        return pd.DataFrame()

df = load_data(uploaded_file)

if uploaded_file is None:
    st.warning("Por favor, importe um arquivo para continuar.")
    st.stop()

if df.empty:
    st.error("Erro: arquivo inválido ou colunas obrigatórias não encontradas.")
    st.stop()

if df['Total (R$)'].isna().mean() > 0.2:
    st.warning("Mais de 20% dos valores da coluna 'Total (R$)' são inválidos e foram convertidos para NaN.")

# Sidebar - filtros
with st.sidebar:
    st.header("Filtros")

    tipos_servico = df['Tipo de Serviço'].dropna().unique()
    tipo_selecionado = st.selectbox("Tipo de Serviço", sorted(tipos_servico))

    fornecedores = df[df['Tipo de Serviço'] == tipo_selecionado]['Fornecedor'].dropna().unique()
    fornecedor_selecionado = st.multiselect("Fornecedores", sorted(fornecedores), default=sorted(fornecedores))

    periodo = df['Mês'].dropna().unique()
    periodo_ordenado = sorted(periodo)
    periodo_selecionado = st.multiselect("Meses", periodo_ordenado, default=periodo_ordenado)

# Aplicar filtros
filtros_aplicados = (
    (df['Tipo de Serviço'] == tipo_selecionado) &
    (df['Fornecedor'].isin(fornecedor_selecionado)) &
    (df['Mês'].isin(periodo_selecionado))
)
df_filtrado = df[filtros_aplicados]

# Tabela interativa
st.subheader("Tabela de Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True, height=600)

# Gráficos

# Total por Tipo de Serviço
st.subheader("Total de Despesas por Tipo de Serviço")
servico_total = df[df['Mês'].isin(periodo_selecionado)].groupby("Tipo de Serviço")["Total (R$)"].sum().reset_index().sort_values(by="Total (R$)", ascending=False)
fig_servico = px.bar(servico_total, x="Tipo de Serviço", y="Total (R$)", text_auto='.2s',
                     title="Total de Despesas por Tipo de Serviço",
                     labels={"Total (R$)": "Total (R$)"})
fig_servico.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
fig_servico.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_servico, use_container_width=True)

# Despesa total por mês
st.subheader("Despesa Total por Mês")
mensal = df_filtrado.groupby("Mês")["Total (R$)"].sum().reset_index()
fig_mensal = px.bar(mensal, x="Mês", y="Total (R$)", text_auto='.2s',
                    labels={"Total (R$)": "Total (R$)"},
                    title=f"Despesas Totais por Mês - {tipo_selecionado}")
fig_mensal.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
fig_mensal.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_mensal, use_container_width=True)

# Despesa por fornecedor
st.subheader("Despesa por Fornecedor")
fornecedor = df_filtrado.groupby("Fornecedor")["Total (R$)"].sum().reset_index().sort_values(by="Total (R$)", ascending=False)
fig_forn = px.bar(fornecedor, x="Fornecedor", y="Total (R$)", text_auto='.2s',
                  title=f"Total de Despesas por Fornecedor - {tipo_selecionado}",
                  labels={"Total (R$)": "Total (R$)"})
fig_forn.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
fig_forn.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_forn, use_container_width=True)

# Top 10 Fornecedores - Percentual
if not fornecedor.empty:
    total_geral = fornecedor["Total (R$)"].sum()
    if total_geral > 0:
        st.subheader("Top 10 Fornecedores - % do Total")
        fornecedor["% do Total"] = (fornecedor["Total (R$)"] / total_geral) * 100
        fornecedor_top10 = fornecedor.head(10)
        fig_top10 = px.bar(fornecedor_top10, x="Fornecedor", y="% do Total", text_auto='.2s',
                           title=f"Top 10 Fornecedores - Percentual do Total - {tipo_selecionado}",
                           labels={"% do Total": "% do Total"})
        fig_top10.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig_top10.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_top10, use_container_width=True)

# Rodapé
st.caption("Desenvolvido por Jefferson • Streamlit + Plotly")
