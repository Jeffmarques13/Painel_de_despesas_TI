import streamlit as st
import pandas as pd

st.set_page_config(page_title="Despesas de TI", layout="wide")
st.title("💼 Controle de Despesas de TI")

# Lê apenas as colunas necessárias (ajuste se precisar de mais)
colunas_usadas = ['Tipo de Serviço', 'Descrição', 'Vence', 'Fornecedor', 'Status']

# Lê o Excel ignorando cabeçalhos automáticos
df = pd.read_excel("despesas_ti.xlsx", header=None)

# Tenta localizar a linha onde começa o conteúdo correto
linha_inicio = 2  # Ajuste se o conteúdo real começar em outra linha

# Seleciona a partir da linha correta e apenas as 5 primeiras colunas
df = df.iloc[linha_inicio:, :5]

# Renomeia as colunas
df.columns = colunas_usadas

# Remove linhas totalmente vazias
df = df.dropna(how='all')

# Prepara dados
df = df.astype(str)
df['Status'] = df['Status'].fillna('')

# Define estilo de cor para vencimentos
def cor_linha(row):
    try:
        dia_venc = int(row['Vence'])
    except:
        return ['background-color: white'] * len(row)
    
    hoje = pd.Timestamp.now().day
    if dia_venc == hoje:
        return ['background-color: orange'] * len(row)
    elif dia_venc < hoje:
        return ['background-color: red; color: white'] * len(row)
    else:
        return ['background-color: green; color: white'] * len(row)

# Exibe no app
st.subheader("📅 Despesas com Vencimentos")
st.dataframe(df.style.apply(cor_linha, axis=1), use_container_width=True)
