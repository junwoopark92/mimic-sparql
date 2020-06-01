from rdflib import Literal, XSD

KG_SCHEMA = {'SUBJECT_ID': ['HADM_ID', 'NAME', 'DOB', 'GENDER', 'EXPIRE_FLAG', 'DOD', 'DOD_YEAR', 'DOB_YEAR'],
          'HADM_ID': ['MARITAL_STATUS', 'AGE', 'LANGUAGE', 'RELIGION', 'ADMISSION_TYPE', 'DAYS_STAY', 'INSURANCE',
                      'ETHNICITY', 'ADMISSION_LOCATION', 'DISCHARGE_LOCATION', 'DIAGNOSIS', 'ADMITYEAR',
                      'ADMITTIME', 'DISCHTIME', 'DIAGNOSES', 'PROCEDURES', 'PRESCRIPTIONS', 'LAB'],
          'DIAGNOSES': ['DIAGNOSES_ICD9_CODE', 'DIAGNOSES_SHORT_TITLE', 'DIAGNOSES_LONG_TITLE'],
          'PROCEDURES': ['PROCEDURES_ICD9_CODE', 'PROCEDURES_SHORT_TITLE', 'PROCEDURES_LONG_TITLE'],
          'PRESCRIPTIONS': ['ICUSTAY_ID', 'DRUG_TYPE', 'DRUG', 'FORMULARY_DRUG_CD', 'ROUTE', 'DRUG_DOSE'],
          'LAB': ['ITEMID', 'CHARTTIME', 'FLAG', 'VALUE_UNIT', 'LABEL', 'FLUID', 'CATEGORY']
          }

SCHEMA = {'PATIENTS': [('ADMISSIONS', 'SUBJECT_ID')],
          'ADMISSIONS': [('DIAGNOSES', 'HADM_ID'), ('PROCEDURES', 'HADM_ID'), ('PRESCRIPTIONS', 'HADM_ID'), ('LAB', 'HADM_ID'), ('PATIENTS', 'SUBJECT_ID')],
          'DIAGNOSES': [('D_ICD_DIAGNOSES', 'ICD9_CODE'), ('ADMISSIONS', 'HADM_ID')],
          'PROCEDURES': [('D_ICD_PROCEDURES', 'ICD9_CODE'), ('ADMISSIONS', 'HADM_ID')],
          'PRESCRIPTIONS': [('ADMISSIONS', 'HADM_ID')],
          'LAB': [('D_LABITEM', 'ITEMID'), ('ADMISSIONS', 'HADM_ID')],
          'D_ICD_DIAGNOSES':[('DIAGNOSES', 'ICD9_CODE')],
          'D_ICD_PROCEDURES':[('PROCEDURES', 'ICD9_CODE')],
          'D_LABITEM':[('LAB', 'ITEMID')],
          }

MAP_WITH_MIMICSQL = {
    'DEMOGRAPHIC': {
        'SUBJECT_ID': 'PATIENTS."SUBJECT_ID"', 'NAME': 'PATIENTS."NAME"', 'HADM_ID': 'ADMISSIONS."HADM_ID"', 'DOB': 'PATIENTS."DOB"',
        'GENDER': 'PATIENTS."GENDER"', 'EXPIRE_FLAG': 'PATIENTS."EXPIRE_FLAG"', 'DOD': 'PATIENTS."DOD"',
        'DOD_YEAR': 'PATIENTS."DOD_YEAR"', 'DOB_YEAR': 'PATIENTS."DOB_YEAR"',
        'MARITAL_STATUS': 'ADMISSIONS."MARITAL_STATUS"', 'AGE': 'ADMISSIONS."AGE"',
        'LANGUAGE': 'ADMISSIONS."LANGUAGE"', 'RELIGION': 'ADMISSIONS."RELIGION"',
        'ADMISSION_TYPE': 'ADMISSIONS."ADMISSION_TYPE"', 'DAYS_STAY': 'ADMISSIONS."DAYS_STAY"',
        'INSURANCE': 'ADMISSIONS."INSURANCE"', 'ETHNICITY': 'ADMISSIONS."ETHNICITY"',
        'ADMISSION_LOCATION': 'ADMISSIONS."ADMISSION_LOCATION"', 'DISCHARGE_LOCATION': 'ADMISSIONS."DISCHARGE_LOCATION"',
        'DIAGNOSIS': 'ADMISSIONS."DIAGNOSIS"', 'ADMITYEAR': 'ADMISSIONS."ADMITYEAR"',
        'ADMITTIME': 'ADMISSIONS."ADMITTIME"', 'DISCHTIME': 'ADMISSIONS."DISCHTIME"'
    },
    'DIAGNOSES': {
        'SUBJECT_ID': 'DIAGNOSES."SUBJECT_ID"',
        'ICD9_CODE': 'DIAGNOSES."ICD9_CODE"', 'SHORT_TITLE': 'D_ICD_DIAGNOSES."SHORT_TITLE"',
        'LONG_TITLE': 'D_ICD_DIAGNOSES."LONG_TITLE"', 'HADM_ID': 'DIAGNOSES."HADM_ID"',
    },
    'PROCEDURES': {
        'SUBJECT_ID': 'PROCEDURES."SUBJECT_ID"',
        'ICD9_CODE': 'PROCEDURES."ICD9_CODE"', 'SHORT_TITLE': 'D_ICD_PROCEDURES."SHORT_TITLE"',
        'LONG_TITLE': 'D_ICD_PROCEDURES."LONG_TITLE"', 'HADM_ID': 'PROCEDURES."HADM_ID"',
    },
    'PRESCRIPTIONS': {
        'SUBJECT_ID':'PRESCRIPTIONS."SUBJECT_ID"',
        'ICUSTAY_ID':'PRESCRIPTIONS."ICUSTAY_ID"', 'DRUG_TYPE':'PRESCRIPTIONS."DRUG_TYPE"',
        'DRUG':'PRESCRIPTIONS."DRUG"', 'FORMULARY_DRUG_CD':'PRESCRIPTIONS."FORMULARY_DRUG_CD"',
        'ROUTE':'PRESCRIPTIONS."ROUTE"', 'DRUG_DOSE':'PRESCRIPTIONS."DRUG_DOSE"', 'HADM_ID': 'PRESCRIPTIONS."HADM_ID"'
    },
    'LAB': {
        'SUBJECT_ID':'LAB."SUBJECT_ID"',
        'ITEMID':'LAB."ITEMID"', 'CHARTTIME':'LAB."CHARTTIME"', 'FLAG':'LAB."FLAG"', 'VALUE_UNIT':'LAB."VALUE_UNIT"',
        'HADM_ID': 'LAB."HADM_ID"',
        'LABEL': 'D_LABITEM."LABEL"', 'FLUID': 'D_LABITEM."FLUID"', 'CATEGORY': 'D_LABITEM."CATEGORY"'
    }
}


patient_demographic_dtype = {
    'SUBJECT_ID':'entity', # root
    'NAME': XSD.string, # sub
    'DOB':XSD.dateTime,  # sub
    'GENDER':XSD.string, # sub
    'EXPIRE_FLAG':XSD.integer, # sub
    'DOD':XSD.dateTime, # sub
    'DOD_YEAR':XSD.float, # sub
    'DOB_YEAR':XSD.integer, # sub
}
hadm_demographic_dtype = {
    'SUBJECT_ID': None,
    'HADM_ID':'entity', # sub
    'MARITAL_STATUS': XSD.string, # hadm
    'AGE': XSD.integer, # hadm
    'LANGUAGE':XSD.string, # hadm
    'RELIGION':XSD.string, # hadm
    'ADMISSION_TYPE':XSD.string, # hadm
    'DAYS_STAY':XSD.integer, # hadm
    'INSURANCE':XSD.string, # hadm
    'ETHNICITY':XSD.string, # hadm
    'ADMISSION_LOCATION':XSD.string,# hadm
    'DISCHARGE_LOCATION':XSD.string, # hadm
    'DIAGNOSIS': XSD.string, # hadm
    'ADMITYEAR':XSD.integer,  # hadm
    'ADMITTIME':XSD.dateTime, # hadm
    'DISCHTIME':XSD.datetime  # hadm
}

diagnoses_dtype = {
    'SUBJECT_ID': None,
    'DIAGNOSES':'entity',# key
    'HADM_ID':'entity', # root
    'DIAGNOSES_ICD9_CODE': XSD.string,
}

d_icd_diagnoses_dtype = {
    'DIAGNOSES_ICD9_CODE': 'entity',
    'DIAGNOSES_SHORT_TITLE': XSD.string,
    'DIAGNOSES_LONG_TITLE': XSD.string,
}

procedures_dtype = {
    'SUBJECT_ID': None,
    'PROCEDURES':'entity',# key
    'HADM_ID':'entity', # root
    'PROCEDURES_ICD9_CODE': 'entity',
}

d_icd_procedures_dtype = {
    'PROCEDURES_ICD9_CODE': 'entity',
    'PROCEDURES_SHORT_TITLE': XSD.string,
    'PROCEDURES_LONG_TITLE': XSD.string,
}

prescriptions_dtype = {
    'SUBJECT_ID': None,
    'PRESCRIPTIONS':'entity',# key
    'HADM_ID':'entity', # root
    'ICUSTAY_ID':'entity',
    'DRUG_TYPE': XSD.string,
    'DRUG': XSD.string,
    'FORMULARY_DRUG_CD': XSD.string,
    'ROUTE':XSD.string,
    'DRUG_DOSE': XSD.string,
}

lab_dtype = {
    'SUBJECT_ID': None,
    'LAB':'entity',# key
    'HADM_ID':'entity', # root
    'ITEMID':'entity',
    'CHARTTIME': XSD.string,
    'FLAG': XSD.string,
    'VALUE_UNIT': XSD.string,
}

d_labitem_dtype = {
    'ITEMID':'entity',
    'LABEL': XSD.string,
    'FLUID': XSD.string,
    'CATEGORY': XSD.string
}

SCHEMA_DTYPE = {**patient_demographic_dtype,
                **hadm_demographic_dtype,
                **diagnoses_dtype,
                **prescriptions_dtype,
                **procedures_dtype,
                **lab_dtype
                }
#print(SCHEMA_DTYPE)
