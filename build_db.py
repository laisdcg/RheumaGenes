import pandas as pd
import sqlite3
import numpy as np
import os

# 1. Carregar o CSV e padronizar cabeçalhos
df = pd.read_csv('TABELA DE GENES.csv')
df.columns = df.columns.str.strip().str.upper()

# Remover genes vazios/nulos na origem para evitar lixo no banco
df = df.dropna(subset=['GENES'])
df['GENES'] = df['GENES'].astype(str).str.strip()

# Identificar a coluna de fontes dinamicamente
source_col = 'SOURCE' if 'SOURCE' in df.columns else 'REFERENCES'
if source_col not in df.columns:
    df[source_col] = 'N/A'

# 2. Criar e conectar ao banco de dados SQLite
conn = sqlite3.connect('rheuma_genes.db')
cursor = conn.cursor()

# 3. Ler o arquivo SQL externo e construir o esquema
if not os.path.exists('schema.sql'):
    raise FileNotFoundError("O arquivo schema.sql não foi encontrado no diretório.")

with open('schema.sql', 'r') as file:
    sql_script = file.read()

cursor.executescript(sql_script)

# Inserir as doenças e resgatar IDs
cursor.execute("INSERT INTO Disease (name) VALUES ('Psoriatic Arthritis')")
cursor.execute("INSERT INTO Disease (name) VALUES ('Ankylosing Spondylitis')")
conn.commit()

psa_id = cursor.execute("SELECT id FROM Disease WHERE name = 'Psoriatic Arthritis'").fetchone()[0]
as_id = cursor.execute("SELECT id FROM Disease WHERE name = 'Ankylosing Spondylitis'").fetchone()[0]

# 4. Processamento Vetorizado e Bulk Insert
genes_df = df[['GENES', 'GENE ACCESSION', 'START POSITION', 'END POSITION', 'CHROMOSOME', 'STRAND', 'DESCRIPTION']].copy()
genes_df = genes_df.replace({np.nan: None})
genes_df = genes_df.drop_duplicates(subset=['GENES'])

cursor.executemany('''
    INSERT INTO Gene (symbol, accession, start_pos, end_pos, chromosome, strand, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', genes_df.values.tolist())

psa_mask = df.get('PSORIASIC ARTHRITIS', pd.Series(dtype=str)).astype(str).str.strip().str.upper() == 'X'
as_mask = df.get('ANKYLOSING SPONDYLITIS', pd.Series(dtype=str)).astype(str).str.strip().str.upper() == 'X'

psa_evidence_df = pd.DataFrame({
    'gene_symbol': df.loc[psa_mask, 'GENES'],
    'disease_id': psa_id,
    'source': df.loc[psa_mask, source_col].astype(str)
})

as_evidence_df = pd.DataFrame({
    'gene_symbol': df.loc[as_mask, 'GENES'],
    'disease_id': as_id,
    'source': df.loc[as_mask, source_col].astype(str)
})

evidence_df = pd.concat([psa_evidence_df, as_evidence_df]).drop_duplicates(subset=['gene_symbol', 'disease_id'])

cursor.executemany('''
    INSERT INTO Gene_Disease_Evidence (gene_symbol, disease_id, source)
    VALUES (?, ?, ?)
''', evidence_df.values.tolist())

conn.commit()
conn.close()

print("Banco de dados 'rheuma_genes.db' reconstruído com sucesso usando schema.sql!")
