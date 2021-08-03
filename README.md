# MIMIC-SPARQL
This repository provides the official mimic-sparql dataset implementation of the following paper: [Knowledge Graph-based Question Answering with Electronic Health Records](https://arxiv.org/abs/2010.09394)
## Example
```
NLQ: how many patients were born before the year 2060?

SQL: select count ( distinct patients."subject_id" ) from patients  where patients."dob_year" < "2060"

SPARQL: select ( count ( distinct ?subject_id ) as ?agg ) where { ?subject_id </dob_year> ?dob_year. filter( ?dob_year < 2060 ).
```

## Prerequisites

1. MIMIC-III   
https://mimic.physionet.org/
2. MIMICSQL  
Paper title: Text-to-SQL Generation for Question Answering on Electronic Medical Records.  
Dataset and codes: https://github.com/wangpinggl/TREQS
3. ENV
```
python 3.6
networkx
rdflib
pandas
numpy
sqlite3  # sqlite is a built-in library from python 2.5. so there is no need to install manually.
requests
```
​	Set up ENV using pip
```bash
pip install networkx rdflib pandas numpy requests
```

## Datasets

1. __MIMICSQL*__  
MIMICSQL* is extended version of MIMICSQL. The database consists of 9 table of MIMIC-III.  
2. __MIMIC-SPARQL__  
MIMIC-SPARQL is a graph-based counterpart of MIMICSQL*. The knowledge graph of this dataset has 173,096 triples and the max hop is 5.

## Guide for creating the MIMICSQL* and MIMIC-SPARQL
0. Prepare MIMIC-III and make mimic.db from MIMICSQL
1. Build mimicsql* database from mimicsql database
2. Build mimic-sparql knowlege graph from mimicsql* database
3. Convert mimicsql SQL query to mimicsql* SQL query
4. Convert mimicsql* SQL query to mimic-sparql SPARQL query


### 0. Prepare MIMIC-III and mimic.db from MIMICSQL
First, you need to access the MIMIC-III data. This requires certification from https://mimic.physionet.org/ 
And then, `mimic.db` is necessary to go to the next step following the https://github.com/wangpinggl/TREQS README.md  

### 1. Build mimicsql* database from mimicsql database
First, you need to save mimic.db under `mimicsql/evaluation/mimic_db` path.
And then, set the current directory in the project root folder, mimic-sparql.
```
python build_mimicsqlstar_db/build_mimicstar_db_from_mimicsql_db.py
```
This is to build MIMICSQL* DB and `mimicsqlstar.db` is made.
### 2. Build mimic-sparql knowlege graph from mimicsql* database
Set the current directory in the project root folder, mimic-sparql.
For building mimic-sparql* from mimicsql*, 
```
python build_mimicsparql_kg/build_complex_kg_from_mimicsqlstar_db.py
```
For building mimic-sparql from mimicsql,
```
python build_mimicsparql_kg/build_simple_kg_from_mimicsql_db.py
```
This is to build MIMIC-SPARQL KG and `mimic_sparqlstar_kg.xml` and `mimic_sparql_kg.xml` are made.
### 3. Convert mimicsql SQL query to mimicsql* SQL query
Set the current directory in the project root folder, mimic-sparql.
```
python convert_mimicsql2sql_dataset.py --dataset_type natural --execution False
python convert_mimicsql2sql_dataset.py --dataset_type template --execution False
```
if set execution as True, the execution results of both queries are compared with each other. 
### 4. Convert mimicsql* SQL query to mimic-sparql SPARQL query
Set the current directory as the project root folder, mimic-sparql.
```
python convert_sql2sparql_dataset.py --dataset_type natural --complex True --execution False
python convert_sql2sparql_dataset.py --dataset_type natural --complex False --execution False

python convert_sql2sparql_dataset.py --dataset_type template --complex True --execution False
python convert_sql2sparql_dataset.py --dataset_type template --complex False --execution False
```
complex option is for selecting simplied schema (mimic-sparql from mimicsql) or original schema (mimic-sparql* from mimicsql*)  
