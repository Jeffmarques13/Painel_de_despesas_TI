import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Despesas de TI", layout="wide")

# Título do app
st.title("💼 Controle de Despesas de TI")

# Carregar o arquivo Excel
arquivo = "despesas_ti.xlsx"  # Substitua pelo caminho correto se necessário

# Leitura com ajuste de cabeçalho correto (ignora as duas primeiras linhas)
df = pd.read_excel(arquivo, header=2)

# Remove colunas totalmente vazias
df = df.dropna(axis=1, how='all')

# Renomeia colunas
df.columns = ['Tipo de Serviço', 'Descrição', 'Vence', 'Fornecedor', 'Status']

# Remove linhas totalmente vazias
df.dropna(how='all', inplace=True)

# Remove espaços extras e normaliza colunas específicas
df['Tipo de Serviço'] = df['Tipo de Serviço'].astype(str).str.strip()
df['Descrição'] = df['Descrição'].astype(str).str.strip()
df['Fornecedor'] = df['Fornecedor'].astype(str).str.strip()
df['Status'] = df['Status'].fillna('')  # Preenche NaN com string vazia

# Função de formatação por vencimento
def cor_linha(row):
    try:
        dia_vencimento = int(row['Vence'])
    except:
        return 'background-color: white'

    hoje = pd.Timestamp.now().day
    if dia_vencimento == hoje:
        return 'background-color: orange'
    elif dia_vencimento < hoje:
        return 'background-color: red; color: white'
    elif dia_vencimento > hoje:
        return 'background-color: green; color: white'
    else:
        return 'background-color: white'

# Exibe a tabela com formatação condicional
st.subheader("📅 Despesas com Vencimentos")
st.dataframe(
    df.style.apply(
        lambda row: [cor_linha(row)] * len(df.columns),
        axis=1
    ),
    use_container_width=True
)
