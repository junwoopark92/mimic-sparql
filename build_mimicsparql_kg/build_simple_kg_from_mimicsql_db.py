import sys
sys.path.append('..')
sys.path.append('.')
import os
from rdflib import Graph, URIRef
import sqlite3
import pandas as pd
from rdflib import Literal
from build_mimicsparql_kg.kg_simple_schema import demographic_dtype, procedures_dtype, prescriptions_dtype,\
    diagnoses_dtype, lab_dtype

PJT_ROOT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
print('PJT_ROOT_PATH: ', PJT_ROOT_PATH)

domain = ''


def isNoneNan(val):
    if val is None:
        return True

    if (type(val) == str) and (val.lower() in ['none', 'nan']):
        return True

    if val != val:
        return True

    return False


def clean_text(val):
    if type(val) == str:
        val = val.replace("\\", ' ')
    return val


def wrap2uri(obj, literal_type):
    obj = obj.lower()
    if literal_type == 'entity':
        return URIRef(obj)

    elif literal_type == 'relation':
        return URIRef(obj)

    else:
        return Literal(clean_text(obj), datatype=literal_type)


def table2triples(df, parent_col, subject_col, col_types):
    triples = []
    for col_name, _ in col_types.items():

        if col_name == parent_col:
            triples += [(wrap2uri(f'{domain}/{col_name}/{sub}', col_types[parent_col]),
                         wrap2uri(f'{domain}/{subject_col}', 'relation'),
                         wrap2uri(f'{domain}/{subject_col}/{obj}', col_types[subject_col]))
                        for (sub, obj) in zip(df[col_name], df[subject_col])]
            continue

        if col_name == subject_col:
            continue

        triples += [(wrap2uri(f'{domain}/{subject_col}/{sub}', col_types[subject_col]),
                     wrap2uri(f'{domain}/{col_name}', 'relation'),
                     wrap2uri(f'{domain}/{col_name}/{obj}' if col_types[col_name] == 'entity' else f'{obj}',
                              col_types[col_name]))
                    for (sub, obj) in zip(df[subject_col], df[col_name]) if not isNoneNan(obj)]

    return triples


if __name__ == '__main__':
    db_conn = sqlite3.connect(os.path.join(PJT_ROOT_PATH, './mimicsql/evaluation/mimic_db/mimic.db'))

    dmographic = pd.read_sql_query("SELECT * FROM demographic", db_conn)
    dmographic.info()

    diagnoses = pd.read_sql_query("SELECT * FROM diagnoses", db_conn)
    diagnoses = diagnoses.reset_index().rename({'index':'DIAGNOSES',
                                                'ICD9_CODE': 'DIAGNOSES_ICD9_CODE',
                                                'SHORT_TITLE':'DIAGNOSES_SHORT_TITLE',
                                                'LONG_TITLE':'DIAGNOSES_LONG_TITLE'}, axis=1)
    diagnoses.info()

    procedures = pd.read_sql_query("SELECT * FROM procedures", db_conn)
    procedures = procedures.reset_index().rename({'index':'PROCEDURES',
                                                  'ICD9_CODE': 'PROCEDURES_ICD9_CODE',
                                                  'SHORT_TITLE': 'PROCEDURES_SHORT_TITLE',
                                                  'LONG_TITLE': 'PROCEDURES_LONG_TITLE'}, axis=1)
    procedures.info()

    prescriptions = pd.read_sql_query("SELECT * FROM prescriptions", db_conn)
    prescriptions = prescriptions.reset_index().rename({'index':'PRESCRIPTIONS'}, axis=1)
    prescriptions['ICUSTAY_ID'] = prescriptions['ICUSTAY_ID'].apply(lambda x: str(x) if x == x else None)
    prescriptions.info()

    lab = pd.read_sql_query("SELECT * FROM lab", db_conn)
    lab = lab.reset_index().rename({'index':'LAB'}, axis=1)
    lab.info()

    triples = []

    triples += table2triples(dmographic, parent_col='', subject_col='HADM_ID', col_types=demographic_dtype)
    print(triples[:5])
    print(triples[-5:])
    print(len(triples))

    triples += table2triples(diagnoses, parent_col='HADM_ID', subject_col='DIAGNOSES', col_types=diagnoses_dtype)
    # print(triples[:5])
    print(triples[-5:])
    print(len(triples))

    triples += table2triples(procedures, parent_col='HADM_ID', subject_col='PROCEDURES', col_types=procedures_dtype)
    # print(triples[:5])
    print(triples[-5:])
    print(len(triples))

    triples += table2triples(prescriptions, parent_col='HADM_ID', subject_col='PRESCRIPTIONS',
                             col_types=prescriptions_dtype)
    # print(triples[:5])
    print(triples[-5:])
    print(len(triples))

    triples += table2triples(lab, parent_col='HADM_ID', subject_col='LAB', col_types=lab_dtype)
    # print(triples[:5])
    print(triples[-5:])
    print(len(triples))

    kg = Graph()
    for i, triple in enumerate(triples):
        kg.add(triple)
    print(len(kg))

    q = """select * where { ?subject_id </gender> "f"^^<http://www.w3.org/2001/XMLSchema#string> }"""
    print(f"TEST QEURY... {q})")
    qres = kg.query(q)
    print("-" * 50)
    for res in qres:
        val = '|'
        for t in res:
            val += str(t.toPython()) + '|\t\t|'
        print(val[:-1])
    print()

    print('SAVE KG ...')
    kg.serialize('./build_mimicsparql_kg/mimic_sparql_kg.xml', format='xml')
    print('SAVE DONE')
    print('LOAD TEST ...')
    kg = Graph()
    kg.parse('./build_mimicsparql_kg/mimic_sparql_kg.xml', format='xml', publicID='/')

    print(len(kg))
    for i, t in enumerate(kg):
        print(i, t)
        if i == 5:
            break

    q = """select ( count ( distinct ?subject_id ) as ?agg )  
    where { ?hadm_id </subject_id> ?subject_id. ?hadm_id </diagnoses> ?diagnoses. 
    ?diagnoses </diagnoses_short_title> "mal neo descend colon"^^<http://www.w3.org/2001/XMLSchema#string>. }"""

    qres = kg.query(q)
    print("-" * 50)
    for res in qres:
        val = '|'
        for t in res:
            val += str(t.toPython()) + '|\t\t|'
        print(val[:-1])
    print()
    print('LOAD DONE')
