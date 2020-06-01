# MIMIC-SPARQL
This is Question-SPARQL pair dataset for Question Answering (QA) for Electronic Health Records (EHR).

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
sqlite3
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
And then, mimic.db is necessary to go to the next step following the https://github.com/wangpinggl/TREQS README.md  

### 1. Build mimicsql* database from mimicsql database
```
python build_mimicstar_db_from_mimicsql_db.py
```
This is to build MIMICSQL* DB.
### 2. Build mimic-sparql knowlege graph from mimicsql* database
```
python build_kg_from_mimicsqlstar_db.py
```
This is to build MIMIC-SPARQL KG.
### 3. Convert mimicsql SQL query to mimicsql* SQL query
```
python convert_mimicsql2sql_dataset.py
```
### 4. Convert mimicsql* SQL query to mimic-sparql SPARQL query
```
python convert_sql2sparql_dataset.py
```
