import streamlit as st
import pandas as pd

st.set_page_config(page_title="Despesas de TI", layout="wide")
st.title("💼 Controle de Despesas de TI")

arquivo = "despesas_ti.xlsx"
df = pd.read_excel(arquivo, header=2)
df = df.dropna(axis=1, how='all')  # Remove colunas vazias
df = df.dropna(how='all')  # Remove linhas vazias

# Verifica quantas colunas existem
st.write("🔍 Colunas detectadas:", df.columns.tolist())

# Só tenta renomear se tiver exatamente 5 colunas
if len(df.columns) == 5:
    df.columns = ['Tipo de Serviço', 'Descrição', 'Vence', 'Fornecedor', 'Status']
else:
    st.error(f"Número inesperado de colunas: {len(df.columns)}. Verifique o arquivo Excel.")
    st.stop()

# Ajusta valores
df = df.astype(str)
df['Status'] = df['Status'].fillna('')

# Formatação
def cor_linha(row):
    try:
        dia_venc = int(row['Vence'])
    except:
        return 'background-color: white'

    hoje = pd.Timestamp.now().day
    if dia_venc == hoje:
        return 'background-color: orange'
    elif dia_venc < hoje:
        return 'background-color: red; color: white'
    else:
        return 'background-color: green; color: white'

# Exibe
st.subheader("📅 Despesas com Vencimentos")
st.dataframe(
    df.style.apply(lambda x: [cor_linha(x)] * len(df.columns), axis=1),
    use_container_width=True
)
