import streamlit as st
import pandas as pd
import sqlite3

# Configuração da página
st.set_page_config(page_title="Catálogo: PsA & AS", layout="wide")

# Função com cache para não sobrecarregar o banco de dados a cada interação
@st.cache_data
def load_data():
    conn = sqlite3.connect('rheuma_genes.db')
    query = '''
        SELECT 
            g.symbol as Gene, 
            g.chromosome as Cromossomo, 
            g.start_pos as Posicao_Inicial,
            g.end_pos as Posicao_Final,
            g.description as Descricao, 
            d.name as Doenca, 
            e.reference as Referencia
        FROM Gene g
        JOIN Gene_Disease_Evidence e ON g.symbol = e.gene_symbol
        JOIN Disease d ON e.disease_id = d.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = load_data()

st.title("🧬 Catálogo Genômico: Artrite Psoriásica e Espondilite Anquilosante")

# Barra lateral (Sidebar) para os inputs de filtro
st.sidebar.header("Filtros de Análise")

busca_gene = st.sidebar.text_input("Buscar Gene (ex: IL22)")

doencas = df['Doenca'].unique()
filtro_doenca = st.sidebar.multiselect("Filtrar por Condição", doencas, default=doencas)

cromossomos = sorted(df['Cromossomo'].dropna().astype(str).unique())
filtro_cromo = st.sidebar.multiselect("Filtrar por Cromossomo", cromossomos)

# Lógica de aplicação dos filtros no dataframe
df_filtrado = df.copy()

if busca_gene:
    df_filtrado = df_filtrado[df_filtrado['Gene'].str.contains(busca_gene.upper(), na=False)]

if filtro_doenca:
    df_filtrado = df_filtrado[df_filtrado['Doenca'].isin(filtro_doenca)]

if filtro_cromo:
    df_filtrado = df_filtrado[df_filtrado['Cromossomo'].isin(filtro_cromo)]

# Métricas rápidas no topo
col1, col2 = st.columns(2)
col1.metric("Anotações Retornadas", len(df_filtrado))
col2.metric("Genes Únicos Retornados", df_filtrado['Gene'].nunique())

# Tabela principal interativa
st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

# Opção para exportar os resultados específicos da busca
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Exportar seleção como CSV",
    data=csv,
    file_name="genes_selecionados.csv",
    mime="text/csv",
)
