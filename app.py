import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Catálogo: PsA & AS", layout="wide")

def query_database(busca_gene, filtro_doenca, busca_desc, filtro_cromo, apenas_interseccao):
    conn = sqlite3.connect('rheuma_genes.db')
    
    # A query extrai todas as colunas da tabela Gene e agrupa as doenças e fontes.
    base_query = '''
        SELECT 
            g.symbol as Gene, 
            g.description as Descricao,
            g.accession as Accession,
            g.chromosome as Cromossomo, 
            g.start_pos as Posicao_Inicial,
            g.end_pos as Posicao_Final,
            GROUP_CONCAT(DISTINCT d.name) as Doencas, 
            GROUP_CONCAT(DISTINCT e.source) as Fontes
        FROM Gene g
        JOIN Gene_Disease_Evidence e ON g.symbol = e.gene_symbol
        JOIN Disease d ON e.disease_id = d.id
        WHERE 1=1
    '''
    params = []
    
    if busca_gene:
        base_query += " AND g.symbol LIKE ?"
        params.append(f"%{busca_gene.upper()}%")
        
    if busca_desc:
        base_query += " AND g.description LIKE ?"
        params.append(f"%{busca_desc}%")
        
    if filtro_cromo:
        placeholders = ', '.join(['?'] * len(filtro_cromo))
        base_query += f" AND g.chromosome IN ({placeholders})"
        params.extend(filtro_cromo)

    # Se a intersecção estrita for exigida, ignoramos o filtro individual de doenças na cláusula WHERE
    # e resolvemos isso no HAVING após o agrupamento.
    if filtro_doenca and not apenas_interseccao:
        placeholders = ', '.join(['?'] * len(filtro_doenca))
        base_query += f" AND d.name IN ({placeholders})"
        params.extend(filtro_doenca)
        
    base_query += " GROUP BY g.symbol, g.accession, g.chromosome, g.start_pos, g.end_pos, g.description"
    
    if apenas_interseccao:
        # Força o retorno apenas de genes que possuam contagem de doenças associadas igual a 2 (PsA e AS)
        base_query += " HAVING COUNT(DISTINCT d.name) = 2"

    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    return df

# Extração de cromossomos únicos para o filtro (execução rápida isolada)
def get_chromosomes():
    conn = sqlite3.connect('rheuma_genes.db')
    df_c = pd.read_sql_query("SELECT DISTINCT chromosome FROM Gene WHERE chromosome IS NOT NULL", conn)
    conn.close()
    # Filtra vazios e ordena
    chromosomes = [c for c in df_c['chromosome'].tolist() if str(c).strip()]
    return sorted(chromosomes, key=lambda x: (str(x).zfill(2) if str(x).isdigit() else x))

st.title("🧬 Catálogo Genômico: Artrite Psoriásica e Espondilite Anquilosante")

st.sidebar.header("Filtros Analíticos")

busca_gene = st.sidebar.text_input("Buscar Gene (Símbolo):")
busca_desc = st.sidebar.text_input("Buscar na Descrição (Palavra-chave):")

doencas_disponiveis = ['Psoriatic Arthritis', 'Ankylosing Spondylitis']
filtro_doenca = st.sidebar.multiselect("Filtrar por Condição:", doencas_disponiveis, default=doencas_disponiveis)

cromossomos_disponiveis = get_chromosomes()
filtro_cromo = st.sidebar.multiselect("Filtrar por Cromossomo:", cromossomos_disponiveis)

st.sidebar.markdown("---")
apenas_interseccao = st.sidebar.checkbox("🔥 Mostrar APENAS genes em comum (Intersecção PsA & AS)", value=False)

# Executa a query com todos os parâmetros da interface
df_filtrado = query_database(busca_gene, filtro_doenca, busca_desc, filtro_cromo, apenas_interseccao)

col1, col2 = st.columns(2)
col1.metric("Anotações Retornadas", len(df_filtrado))
col2.metric("Genes Únicos", df_filtrado['Gene'].nunique())

st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

if not df_filtrado.empty:
    st.download_button(
        label="Exportar Tabela Atual (CSV)",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="catalogo_genes_filtrado.csv",
        mime="text/csv",
    )
