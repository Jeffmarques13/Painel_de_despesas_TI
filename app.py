import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tratador de Despesas", layout="centered")

st.title("💼 Tratamento de Planilha de Despesas")

# Upload do arquivo
arquivo = st.file_uploader("📁 Envie sua planilha Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo, sheet_name=0)
    st.write("Colunas na planilha:", df.columns.tolist())
    
    # Convertendo datas
    df['Vence'] = pd.to_datetime(df['Vence'], errors='coerce')

    st.subheader("📊 Visualização da Planilha Original")
    st.dataframe(df)

    st.markdown("---")

    # Filtros
    st.subheader("📅 Filtro por Período de Vencimento")
    data_inicio = st.date_input("Data Início", value=datetime.today())
    data_fim = st.date_input("Data Fim", value=datetime.today())

    st.subheader("🔍 Filtro por palavra-chave (Fornecedor ou Serviço)")
    palavra = st.text_input("Palavra-chave para excluir (opcional)").lower()

    # Aplicar filtros
    df_filtrado = df[(df['Vencimento'] >= pd.to_datetime(data_inicio)) & 
                     (df['Vencimento'] <= pd.to_datetime(data_fim))]

    if palavra:
        df_filtrado = df_filtrado[
            ~df_filtrado['Fornecedor'].str.lower().str.contains(palavra) &
            ~df_filtrado['Serviço'].str.lower().str.contains(palavra)
        ]

    # Marcar como pago
    if st.checkbox("✅ Marcar todos como 'Pago'"):
        df_filtrado['Status'] = 'Pago'

    st.subheader("📋 Resultado Tratado")
    st.dataframe(df_filtrado)

    # Exportar planilha
    def to_excel(df):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tratado')
        return output.getvalue()

    excel_bytes = to_excel(df_filtrado)
    st.download_button("📥 Baixar Planilha Tratada", data=excel_bytes,
                       file_name="Despesas_Tratadas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
