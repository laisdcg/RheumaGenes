import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Catálogo: PsA & AS", layout="wide")

def query_database(gene_search, selected_diseases):
    # Conexão com o banco de dados local carregado no Streamlit Cloud
    conn = sqlite3.connect('rheuma_genes.db')
    
    # Query ajustada para o esquema real do seu banco (Gene_Disease_Evidence)
    base_query = '''
        SELECT 
            g.symbol as Gene, 
            g.chromosome as Cromossomo, 
            d.name as Doenca, 
            GROUP_CONCAT(e.source, '; ') as Fontes
        FROM Gene g
        JOIN Gene_Disease_Evidence e ON g.symbol = e.gene_symbol
        JOIN Disease d ON e.disease_id = d.id
        WHERE 1=1
    '''
    params = []
    
    if gene_search:
        base_query += " AND g.symbol LIKE ?"
        params.append(f"%{gene_search.upper()}%")
        
    if selected_diseases:
        placeholders = ', '.join(['?'] * len(selected_diseases))
        base_query += f" AND d.name IN ({placeholders})"
        params.extend(selected_diseases)
        
    base_query += " GROUP BY g.symbol, g.chromosome, d.name"
    
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    return df

st.title("🧬 Catálogo Genômico: Artrite Psoriásica e Espondilite Anquilosante")

st.sidebar.header("Filtros Analíticos")

# Inputs
busca_gene = st.sidebar.text_input("Buscar Gene (ex: IL22)")

# Doenças padronizadas conforme a inserção no banco
doencas_disponiveis = ['Psoriatic Arthritis', 'Ankylosing Spondylitis']
filtro_doenca = st.sidebar.multiselect("Filtrar por Condição", doencas_disponiveis, default=doencas_disponiveis)

# O slider de FDR foi removido, pois seus dados atuais não o suportam.

# Execução dinâmica da query
df_filtrado = query_database(busca_gene, filtro_doenca)

# Métricas
col1, col2 = st.columns(2)
col1.metric("Anotações Retornadas", len(df_filtrado))
col2.metric("Genes Únicos", df_filtrado['Gene'].nunique())

st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

if not df_filtrado.empty:
    st.download_button(
        label="Exportar Matriz Filtrada (CSV)",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="matriz_transcriptomica_filtrada.csv",
        mime="text/csv",
    )
