## RheumaGenes: Genomic Catalog for PsA and AS

## Visão Geral
Este repositório está sendo construído desde 2023 e contém o pipeline de estruturação e a interface de exploração de um catálogo genômico focado em Artrite Psoriásica (PsA) e Espondilite Anquilosante (AS). O sistema automatiza a conversão de um arquivo plano de curadoria manual para um banco de dados relacional SQLite e disponibiliza uma aplicação web interativa em Streamlit.

## Contexto da Pesquisa
O banco de dados serve como base curada para investigações de transcriptômica e modelagem de redes biológicas conduzidas no escopo da pós-graduação em Bioinformática (BioME/UFRN). O catálogo estruturado funciona como conjunto de validação para pipelines de análise de RNA-Seq, facilitando o cruzamento de marcadores exclusivos e compartilhados entre os fenótipos articulares.

## Arquitetura de Dados
O banco `rheuma_genes.db` opera com a seguinte modelagem relacional:
* **Gene:** Tabela primária com anotações genômicas (Symbol, Accession, Start/End Position, Chromosome).
* **Disease:** Entidades fenotípicas estáticas.
* **Gene_Disease_Evidence:** Tabela associativa que vincula genes às doenças, armazenando as evidências e referências bibliográficas.

## Requisitos do Ambiente
A infraestrutura foi construída em Python. Para instalar as dependências necessárias, execute:
```bash
pip install pandas sqlite3 streamlit
