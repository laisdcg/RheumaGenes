DROP TABLE IF EXISTS Gene_Disease_Evidence;
DROP TABLE IF EXISTS Disease;
DROP TABLE IF EXISTS Gene;

CREATE TABLE Gene (
    symbol TEXT PRIMARY KEY,
    accession TEXT,
    start_pos INTEGER,
    end_pos INTEGER,
    chromosome TEXT,
    strand TEXT,
    description TEXT
);

CREATE TABLE Disease (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE Gene_Disease_Evidence (
    gene_symbol TEXT,
    disease_id INTEGER,
    source TEXT,
    FOREIGN KEY(gene_symbol) REFERENCES Gene(symbol),
    FOREIGN KEY(disease_id) REFERENCES Disease(id),
    PRIMARY KEY (gene_symbol, disease_id)
);
