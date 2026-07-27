import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Catálogo: PsA & AS", layout="wide")

# Função que executa buscas parametrizadas diretamente no banco
def query_database(gene_search, selected_diseases, fdr_threshold):
    conn = sqlite3.connect('rheuma_genes.db')
    
    # A query agora exige dados quantitativos (logFC e FDR) que DEVEM estar no banco
    base_query = '''
        SELECT 
            g.symbol as Gene, 
            g.chromosome as Cromossomo, 
            d.name as Doenca, 
            e.logfc as Log2FoldChange,
            e.fdr as FDR,
            GROUP_CONCAT(e.source, '; ') as Fontes
        FROM Gene g
        JOIN Expression_Result e ON g.symbol = e.gene_symbol
        JOIN Disease d ON e.study_id = d.id -- Ajustado para refletir a tabela relacional correta
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
        
    # Filtro aplicado diretamente no banco de dados
    base_query += " AND e.fdr <= ?"
    params.append(fdr_threshold)
    
    base_query += " GROUP BY g.symbol, g.chromosome, d.name, e.logfc, e.fdr"
    
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    return df

st.title("🧬 Catálogo Genômico: Artrite Psoriásica e Espondilite Anquilosante")

st.sidebar.header("Filtros Analíticos")

# Inputs
busca_gene = st.sidebar.text_input("Buscar Gene (ex: IL22)")

# O ideal é extrair isso do banco via query, mas mantido estático para exemplo
doencas_disponiveis = ['Psoriatic Arthritis', 'Ankylosing Spondylitis']
filtro_doenca = st.sidebar.multiselect("Filtrar por Condição", doencas_disponiveis, default=doencas_disponiveis)

# Novo filtro estrito
filtro_fdr = st.sidebar.slider("FDR Máximo Permitido (Significância)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

# Executa a query apenas quando necessário, trazendo dados já reduzidos
df_filtrado = query_database(busca_gene, filtro_doenca, filtro_fdr)

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
