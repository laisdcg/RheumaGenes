import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Catalog: PsA & AS", layout="wide")

def query_database(busca_gene, filtro_doenca, busca_desc, filtro_cromo, apenas_interseccao):
    conn = sqlite3.connect('rheuma_genes.db')
    
    base_query = '''
        SELECT 
            g.symbol as Gene, 
            g.description as Description,
            g.accession as Accession,
            g.chromosome as Chromosome, 
            g.strand as Strand,
            g.start_pos as Starting_Position,
            g.end_pos as Final_Position,
            GROUP_CONCAT(DISTINCT d.name) as Disease, 
            GROUP_CONCAT(DISTINCT e.source) as Source
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

    if filtro_doenca and not apenas_interseccao:
        placeholders = ', '.join(['?'] * len(filtro_doenca))
        base_query += f" AND d.name IN ({placeholders})"
        params.extend(filtro_doenca)
        
    base_query += " GROUP BY g.symbol, g.accession, g.chromosome, g.strand, g.start_pos, g.end_pos, g.description"
    
    if apenas_interseccao:
        base_query += " HAVING COUNT(DISTINCT d.name) = 2"

    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    return df

def get_chromosomes():
    conn = sqlite3.connect('rheuma_genes.db')
    df_c = pd.read_sql_query("SELECT DISTINCT chromosome FROM Gene WHERE chromosome IS NOT NULL", conn)
    conn.close()
    chromosomes = [c for c in df_c['chromosome'].tolist() if str(c).strip()]
    return sorted(chromosomes, key=lambda x: (str(x).zfill(2) if str(x).isdigit() else x))

st.title("🧬 RheumaGenes: Genomic Catalog for PsA and AS")

st.sidebar.header("Analytical Filters")

busca_gene = st.sidebar.text_input("Search for Gene (Symbol):")
busca_desc = st.sidebar.text_input("Search in Description (Keyword):")

doencas_disponiveis = ['Psoriatic Arthritis', 'Ankylosing Spondylitis']
filtro_doenca = st.sidebar.multiselect("Filter by Condition:", doencas_disponiveis, default=doencas_disponiveis)

cromossomos_disponiveis = get_chromosomes()
filtro_cromo = st.sidebar.multiselect("Filter by Chromosome:", cromossomos_disponiveis)

st.sidebar.markdown("---")
apenas_interseccao = st.sidebar.checkbox("🔥 Show ONLY genes in common (Intersection of PsA & AS)", value=False)

df_filtrado = query_database(busca_gene, filtro_doenca, busca_desc, filtro_cromo, apenas_interseccao)

col1, col2 = st.columns(2)
col1.metric("Returned Notes", len(df_filtrado))
col2.metric("Unique Genes", df_filtrado['Gene'].nunique())

st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

if not df_filtrado.empty:
    st.download_button(
        label="Export Current Table (CSV)",
        data=df_filtrado.to_csv(index=False).encode('utf-8'),
        file_name="catalogo_genes_filtrado.csv",
        mime="text/csv",
    )

st.markdown("---")
st.subheader("📚 Legend for Bibliographic References")

with st.expander("Expand to view the mapping of the sources cited in the table"):
    st.markdown("""
    | ID | Platform | GEO / PMC Access | PubMed Identifier (PMID) |
    |---|---|---|---|
    | **1** | Enrichr | [maayanlab.cloud/Enrichr](https://maayanlab.cloud/Enrichr/) | - |
    | **2** | RummaGEO | [GSE205748](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE205748) | [37131254](https://pubmed.ncbi.nlm.nih.gov/37131254/), [37137278](https://pubmed.ncbi.nlm.nih.gov/37137278/) |
    | **3** | RummaGEO | [GSE137510](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137510) | [31677365](https://pubmed.ncbi.nlm.nih.gov/31677365/) |
    | **4** | RummaGEO | [GSE220130](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE220130) | - |
    | **5** | RummaGEO | [GSE221786](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE221786) | - |
    | **6** | RummaGEO | [GSE141646](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141646) | [28835680](https://pubmed.ncbi.nlm.nih.gov/28835680/) |
    | **7** | RummaGEO | [GSE212613](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE212613) | [36246583](https://pubmed.ncbi.nlm.nih.gov/36246583/) |
    | **8** | RummaGEO | [GSE205812](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE205812) | [38622662](https://pubmed.ncbi.nlm.nih.gov/38622662/), [37254181](https://pubmed.ncbi.nlm.nih.gov/37254181/) |
    | **9** | Rummagene | [PMC10055600](https://pmc.ncbi.nlm.nih.gov/articles/PMC10055600/) | - |
    | **10** | Rummagene | [PMC10129963](https://pmc.ncbi.nlm.nih.gov/articles/PMC10129963/) | - |
    | **11** | Rummagene | [PMC10152590](https://pmc.ncbi.nlm.nih.gov/articles/PMC10152590/) | - |
    | **12** | Rummagene | [PMC10216275](https://pmc.ncbi.nlm.nih.gov/articles/PMC10216275/) | - |
    | **13** | Rummagene | [PMC10226212](https://pmc.ncbi.nlm.nih.gov/articles/PMC10226212/) | - |
    | **14** | Rummagene | [PMC10594069](https://pmc.ncbi.nlm.nih.gov/articles/PMC10594069/) | - |
    | **15** | Rummagene | [PMC10641465](https://pmc.ncbi.nlm.nih.gov/articles/PMC10641465/) | - |
    | **16** | Rummagene | [PMC10711358](https://pmc.ncbi.nlm.nih.gov/articles/PMC10711358/) | - |
    | **17** | Rummagene | [PMC10731026](https://pmc.ncbi.nlm.nih.gov/articles/PMC10731026/) | - |
    | **18** | Rummagene | [PMC10790246](https://pmc.ncbi.nlm.nih.gov/articles/PMC10790246/) | - |
    """)
