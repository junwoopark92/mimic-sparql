from rdflib import Literal, XSD

KG_SCHEMA = {'SUBJECT_ID': ['HADM_ID', 'NAME', 'DOB', 'GENDER', 'EXPIRE_FLAG', 'DOD', 'DOD_YEAR', 'DOB_YEAR'],
          'HADM_ID': ['MARITAL_STATUS', 'AGE', 'LANGUAGE', 'RELIGION', 'ADMISSION_TYPE', 'DAYS_STAY', 'INSURANCE',
                      'ETHNICITY', 'ADMISSION_LOCATION', 'DISCHARGE_LOCATION', 'DIAGNOSIS', 'ADMITYEAR',
                      'ADMITTIME', 'DISCHTIME', 'DIAGNOSES', 'PROCEDURES', 'PRESCRIPTIONS', 'LAB'],
          'DIAGNOSES': ['DIAGNOSES_ICD9_CODE'],
          'DIAGNOSES_ICD9_CODE': ['DIAGNOSES_SHORT_TITLE', 'DIAGNOSES_LONG_TITLE'],
          'PROCEDURES': ['PROCEDURES_ICD9_CODE'],
          'PROCEDURES_ICD9_CODE': ['PROCEDURES_SHORT_TITLE', 'PROCEDURES_LONG_TITLE'],
          'PRESCRIPTIONS': ['ICUSTAY_ID', 'DRUG_TYPE', 'DRUG', 'FORMULARY_DRUG_CD', 'ROUTE', 'DRUG_DOSE'],
          'LAB': ['ITEMID', 'CHARTTIME', 'FLAG', 'VALUE_UNIT'],
          'ITEMID' :['LABEL', 'FLUID', 'CATEGORY']
          }


patients_dtype = {
    'SUBJECT_ID':'entity', # root
    'NAME': XSD.string, # sub
    'DOB':XSD.dateTime,  # sub
    'GENDER':XSD.string, # sub
    'EXPIRE_FLAG':XSD.integer, # sub
    'DOD':XSD.dateTime, # sub
    'DOD_YEAR':XSD.float, # sub
    'DOB_YEAR':XSD.integer, # sub
}
addmissions_dtype = {
    'SUBJECT_ID':'entity',
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
    'DIAGNOSES':'entity',# key
    'HADM_ID':'entity', # root
    'DIAGNOSES_ICD9_CODE': 'entity'
}

d_icd_diagnoses_dtype = {
    'DIAGNOSES_ICD9_CODE': 'entity',
    'DIAGNOSES_SHORT_TITLE': XSD.string,
    'DIAGNOSES_LONG_TITLE': XSD.string,
}

procedures_dtype = {
    'PROCEDURES':'entity',# key
    'HADM_ID':'entity', # root
    'PROCEDURES_ICD9_CODE':'entity'
}

d_icd_procedures_dtype = {
    'PROCEDURES_ICD9_CODE': 'entity',
    'PROCEDURES_SHORT_TITLE': XSD.string,
    'PROCEDURES_LONG_TITLE': XSD.string,
}

prescriptions_dtype = {
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
    'LAB':'entity',# key
    'HADM_ID':'entity', # root
    'ITEMID':'entity',
    'CHARTTIME': XSD.string,
    'FLAG': XSD.string,
    'VALUE_UNIT': XSD.string
}

d_labitem_dtype = {
    'ITEMID':'entity',
    'LABEL': XSD.string,
    'FLUID': XSD.string,
    'CATEGORY': XSD.string
}

SCHEMA_DTYPE = {**patients_dtype,
                **addmissions_dtype,
                **diagnoses_dtype,
                **d_icd_diagnoses_dtype,
                **prescriptions_dtype,
                **procedures_dtype,
                **d_icd_procedures_dtype,
                **lab_dtype,
                **d_labitem_dtype,
                }

#print(SCHEMA_DTYPE)
