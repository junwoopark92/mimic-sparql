import sys
sys.path.append('..')
sys.path.append('.')
import os
import pandas as pd
import sqlite3

from build_mimicsqlstar_db.schema_mimic import *
from mimicsql.evaluation.utils import query

PJT_ROOT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
print('PJT_ROOT_PATH: ',PJT_ROOT_PATH)

if __name__ == '__main__':
    db_conn = sqlite3.connect(os.path.join(PJT_ROOT_PATH, 'mimicsql/evaluation/mimic_db/mimic.db'))

    patient_cols = list(patient_demographic_dtype.keys())
    addmission_cols = list(hadm_demographic_dtype.keys())

    demographic = pd.read_sql_query("SELECT * FROM DEMOGRAPHIC", db_conn)
    demographic.info()
    demographic.head()

    patients_df = demographic.loc[:,patient_cols]
    patients_df.info()

    addmissions_df = demographic.loc[:,addmission_cols] # primary key: HADM_ID
    addmissions_df.info()

    diagenoses = pd.read_sql_query("SELECT * FROM DIAGNOSES", db_conn)
    diagenoses = diagenoses.reset_index().rename({'index': 'DIAGNOSES'}, axis=1)
    diagenoses.info()

    diagnoses_cols = list(diagnoses_dtype.keys())
    d_icd_dagnoses_cols = list(d_icd_diagnoses_dtype.keys())
    diagnoses_cols = ['ICD9_CODE' if c == 'DIAGNOSES_ICD9_CODE' else c for c in diagnoses_cols]
    d_icd_dagnoses_cols = ['ICD9_CODE' if c == 'DIAGNOSES_ICD9_CODE' else c for c in d_icd_dagnoses_cols]
    d_icd_dagnoses_cols = ['LONG_TITLE' if c == 'DIAGNOSES_LONG_TITLE' else c for c in d_icd_dagnoses_cols]
    d_icd_dagnoses_cols = ['SHORT_TITLE' if c == 'DIAGNOSES_SHORT_TITLE' else c for c in d_icd_dagnoses_cols]

    diagenoses_df = diagenoses.loc[:, diagnoses_cols]
    diagenoses_df.info()

    d_icd_diagenoses_df = diagenoses.loc[:, d_icd_dagnoses_cols]
    d_icd_diagenoses_df.drop_duplicates(inplace=True)
    d_icd_diagenoses_df.reset_index(inplace=True, drop=True)
    d_icd_diagenoses_df.info()

    procedures = pd.read_sql_query("SELECT * FROM PROCEDURES", db_conn)
    procedures = procedures.reset_index().rename({'index': 'PROCEDURES'}, axis=1)
    procedures.info()

    procedures_cols = list(procedures_dtype.keys())
    d_icd_procedures_cols = list(d_icd_procedures_dtype.keys())
    procedures_cols = ['ICD9_CODE' if c == 'PROCEDURES_ICD9_CODE' else c for c in procedures_cols]
    d_icd_procedures_cols = ['ICD9_CODE' if c == 'PROCEDURES_ICD9_CODE' else c for c in d_icd_procedures_cols]
    d_icd_procedures_cols = ['LONG_TITLE' if c == 'PROCEDURES_LONG_TITLE' else c for c in d_icd_procedures_cols]
    d_icd_procedures_cols = ['SHORT_TITLE' if c == 'PROCEDURES_SHORT_TITLE' else c for c in d_icd_procedures_cols]

    procedures_df = procedures.loc[:, procedures_cols]
    procedures_df.info()

    d_icd_procedures_df = procedures.loc[:, d_icd_procedures_cols]
    d_icd_procedures_df.drop_duplicates(inplace=True)
    d_icd_procedures_df.reset_index(inplace=True, drop=True)
    d_icd_procedures_df.info()

    lab_cols = list(lab_dtype.keys())
    d_labitem_cols = list(d_labitem_dtype.keys())

    lab = pd.read_sql_query("SELECT * FROM LAB", db_conn)
    lab = lab.reset_index().rename({'index': 'LAB'}, axis=1)
    lab.info()

    lab_df = lab.loc[:, lab_cols]
    lab_df.info()

    d_labitem_df = lab.loc[:, d_labitem_dtype]
    d_labitem_df.drop_duplicates(inplace=True)
    d_labitem_df.reset_index(inplace=True, drop=True)
    d_labitem_df.info()

    prescriptions_cols = list(prescriptions_dtype.keys())

    prescriptions = pd.read_sql_query("SELECT * FROM PRESCRIPTIONS", db_conn)
    prescriptions = prescriptions.reset_index().rename({'index': 'PRESCRIPTIONS'}, axis=1)
    prescriptions_df = prescriptions.loc[:, prescriptions_cols]
    prescriptions_df.info()

    conn = sqlite3.connect(os.path.join(PJT_ROOT_PATH ,'build_mimicsqlstar_db/', 'mimicsqlstar.db')) 

    patients_df.to_sql('PATIENTS', conn, if_exists='replace', index=False)
    addmissions_df.to_sql('ADMISSIONS', conn, if_exists='replace', index=False)
    diagenoses_df.to_sql('DIAGNOSES', conn, if_exists='replace', index=False)
    d_icd_diagenoses_df.to_sql('D_ICD_DIAGNOSES', conn, if_exists='replace', index=False)
    procedures_df.to_sql('PROCEDURES', conn, if_exists='replace', index=False)
    d_icd_procedures_df.to_sql('D_ICD_PROCEDURES', conn, if_exists='replace', index=False)
    prescriptions_df.to_sql('PRESCRIPTIONS', conn, if_exists='replace', index=False)
    lab_df.to_sql('LAB', conn, if_exists='replace', index=False)
    d_labitem_df.to_sql('D_LABITEM', conn, if_exists='replace', index=False)

    print(f'LOAD DB ...')

    db_file = os.path.join(PJT_ROOT_PATH,'build_mimicsqlstar_db/mimicsqlstar.db')
    new_model = query(db_file)
    print('DONE')

    test_sql = ["""select distinct patients."subject_id",  admissions."hadm_id"
                from patients
                inner join admissions on patients."subject_id" = admissions."subject_id"
                inner join diagnoses on admissions."hadm_id" = diagnoses."hadm_id"
                inner join prescriptions on admissions.hadm_id = prescriptions.hadm_id
                inner join d_icd_diagnoses on d_icd_diagnoses.icd9_code = diagnoses.icd9_code
                where d_icd_diagnoses."short_title" = "crnry athrscl natve vssl" 
                and prescriptions."drug_type" = "main"
                """,
                """select count (distinct patients.subject_id ) from patients where patients.dob_year < 2060
                """,
                """select distinct patients."subject_id",  admissions."hadm_id"
                   from patients
                   inner join admissions on patients.subject_id = admissions.subject_id
                """,
                """select distinct patients."subject_id",  admissions."hadm_id"
                   from patients
                   inner join admissions on patients.subject_id = admissions.subject_id
                """]

    for sql in test_sql:
        print(sql)
        sql_res = new_model.execute_sql(sql).fetchall()
        for res in sql_res:
            val = '|'
            temp = []
            for t in res:
                val += str(t) + '|\t\t|'
                temp.append(str(t))
            print(val[:-1])
        print()

