import sys
import networkx as nx
import json
import os
import re
import numpy as np
import pandas as pd
from rdflib import Graph
from sql2sparql import SQL2SPARQL, sparql_postprocessing, join_entity
from mimicsql.evaluation.utils import query
from build_mimicsparql_kg.build_kg_from_mimicsqlstar_db import clean_text


def split_triples(sparql):
    try:
        select_part, where_part = sparql.split(' where ')
    except:
        print(sparql)
        select_part, where_part = sparql.split(' where ')[0], sparql.split(' where ')[-1]

    where_part = where_part.replace('{','').replace('}','')
    triple = [t.strip() for t in where_part.split('. ')]
    return select_part, [t for t in triple if len(t) != 0]


def none2zero(answer):
    if answer is None:
        return 0.0

    if type(answer) != str:
        return answer

    if answer.lower() == 'none':
        return 0.0

    try:
        answer = float(answer)
    except:
        pass

    return answer


def answer_normalization(answers):
    if len(answers) == 0:
        answers = [(0.0, )]
    return [tuple([none2zero(val) for val in answer]) for answer in answers]


def entity2value(entity):
    match = re.findall('/[a-z_\d]+/[a-z\d]+', entity)
    if len(match) > 0:
        return re.sub('/[a-z_\d]+/', '', entity)
    else:
        return entity


def replace_cond_val(q):
    q = re.sub(' "[^"]*"', ' <cond>', q)
    q = re.sub('[>=<]+ [0-9]+ ', '<cond> ', q)
    q = re.sub('</[a-z_]+/[\d]+>', '<cond>', q)
    return q


def isequal(sql_answer, sparql_answer):
    sql_answer = [row for row in sql_answer if 'None' not in row]
    sql_answer = [tuple([clean_text(a.lower()) if type(a) == str else a for a in row]) for row in sql_answer]

    sparql_answer = [tuple([entity2value(a) if type(a) == str else a for a in row]) for row in sparql_answer]

    if set(sql_answer) == set(sparql_answer): #set의 결과가 같다면 정답
        return True

    sparql_answer = answer_normalization(sparql_answer)
    sql_answer = answer_normalization(sql_answer)

    if set(sql_answer) == set(sparql_answer):
        return True

    return False


def check_no_cond_val(sparql):
    cond = []
    cond += re.findall('\^\^<http://', sparql) # value
    cond += re.findall('</[a-z_]+/[\d]+>', sparql) # entity
    cond += re.findall('"[a-z\d ]+"', sparql) # value
    cond += re.findall('filter', sparql) # fiter
    if len(cond) == 0:
        return True
    else:
        return False


def n_inner_join(x):
    return len(re.findall('inner join', x))


def compare_sql_and_spqral_pred():
    datadir = '../TREQS/mimicsql_data/mimicnormal_natural/'
    filename = 'test.json'
    outputdir = '../TREQS/evaluation/generated_sql/'
    output_filename = 'output.json'

    covertor = SQL2SPARQL()
    print('LOAD output.json')
    sparql_preds = []
    sparql_golds = []
    with open(os.path.join(outputdir, output_filename)) as json_file:
        for line in json_file:
            dic = json.loads(line)
            sparql_preds.append(dic['sql_pred'])
            sparql_golds.append(dic['sql_gold'])
    print('DONE')

    data = []
    with open(os.path.join(datadir, filename)) as json_file:
        for line in json_file:
            data.append(json.loads(line))

    df = pd.DataFrame(data)

    print('LOAD DB ...')
    db_file = './evaluation/mimic_db/mimic_normal.db'
    model = query(db_file)
    print('DONE')

    print('LOAD KG ...')
    kg = Graph()
    kg.parse('./evaluation/mimic_kg.xml', format='xml', publicID='/')
    print('DONE')

    lf_permu_correct = 0
    lf_permu_cond_correct = 0
    lf_correct = 0
    gold_correct = 0
    pred_correct = 0
    ablation_results = []
    for i, sql in enumerate(df['sql']):
        ablation_dic = {}
        sql = sql.lower()

        sql_answer = []
        sparql_pred_answer = []
        sparql_gold_answer = []

        print("-" * 50)
        print(i, sql)

        ablation_dic['n_inner'] = n_inner_join(sql)
        ablation_dic['n_hop'] = covertor.get_max_hop(sql)

        sql_res = model.execute_sql(sql).fetchall()
        for res in sql_res:
            val = '|'
            temp = []
            for t in res:
                val += str(t) + '|\t\t|'
                temp.append(str(t))
            print(val[:-1])
            sql_answer.append(tuple(temp))
        print()

        sparql_pred = sparql_preds[i]
        sparql_gold = sparql_golds[i]

        sparql_pred = sparql_postprocessing(sparql_pred)
        sparql_pred = join_entity(sparql_pred)
        sparql_gold = sparql_postprocessing(sparql_gold)
        sparql_gold = join_entity(sparql_gold)

        # if replace_cond_val(sparql_pred) == replace_cond_val(sparql_gold):
        #     lf_correct += 1

        if sparql_pred == sparql_gold:
            lf_correct += 1

        cond_sp = replace_cond_val(sparql_pred)
        cond_sg = replace_cond_val(sparql_gold)
        cond_sps, cond_spw = split_triples(cond_sp)
        cond_sgs, cond_sgw = split_triples(cond_sg)

        sps, spw = split_triples(sparql_pred)
        sgs, sgw = split_triples(sparql_gold)

        if cond_sps == cond_sgs and set(cond_spw) == set(cond_sgw):
            lf_permu_cond_correct += 1
            ablation_dic['lf_cond_invar_correct'] = 1

        if sps == sgs and set(spw) == set(sgw):
            lf_permu_correct += 1
            ablation_dic['lf_correct'] = 1

        print(i, sparql_gold)
        sparql_res = kg.query(sparql_gold)
        for res in sparql_res:
            val = '|'
            temp = []
            for t in res:
                val += str(t.toPython()) + '|\t\t|'
                temp.append(str(t.toPython()))
            print(val[:-1])
            sparql_gold_answer.append(tuple(temp))
        print(sql_answer, sparql_gold_answer, isequal(sql_answer, sparql_gold_answer))

        if isequal(sql_answer, sparql_gold_answer):
            gold_correct += 1
        else:
            print('sql gold false')

        print(i, sparql_pred)

        if check_no_cond_val(sparql_pred):
            print(f'[NO COND]: {sparql_pred}')
            print()
            ablation_results.append(ablation_dic)
            continue

        try:
            sparql_res = kg.query(sparql_pred)
            for res in sparql_res:
                val = '|'
                temp = []
                for t in res:
                    val += str(t.toPython()) + '|\t\t|'
                    temp.append(str(t.toPython()))
                print(val[:-1])
                sparql_pred_answer.append(tuple(temp))
            print(sql_answer, sparql_pred_answer, isequal(sql_answer, sparql_pred_answer))

            if isequal(sql_answer, sparql_pred_answer):
                ablation_dic['ex_correct'] = 1
                pred_correct += 1

        except:
            print("syntax error")

        ablation_results.append(ablation_dic)

        print()

    print(f'[SQL2SPARQL] filenmae: {filename}, Answer Accuracy: {gold_correct / len(data):.4f}')
    print(f'[SQL2SPARQL] filenmae: {output_filename}, Answer Accuracy: {pred_correct / len(data):.4f}')
    print(f'[SQL2SPARQL] filenmae: {output_filename}, Logic Form Accuracy: {lf_correct / len(data):.4f}')
    print(f'[SQL2SPARQL] filenmae: {output_filename}, Logic Form Accuracy*: {lf_permu_correct / len(data):.4f}')
    print(f'[SQL2SPARQL] filenmae: {output_filename}, Logic Form Cond Invariant Accuracy*: {lf_permu_cond_correct / len(data):.4f}')

    df = pd.DataFrame(ablation_results)
    df.fillna(0, inplace=True)
    df.info()
    print(df['n_inner'].value_counts())
    print(df[df['n_inner'] == 0]['ex_correct'].sum())
    print(df[df['n_inner'] == 1]['ex_correct'].sum())
    print(df[df['n_inner'] == 2]['ex_correct'].sum())

    print('*'*50)
    print(df['n_hop'].value_counts())
    print(df[df['n_hop'] == 1]['ex_correct'].sum())
    print(df[df['n_hop'] == 2]['ex_correct'].sum())
    print(df[df['n_hop'] == 3]['ex_correct'].sum())
    print(df[df['n_hop'] == 4]['ex_correct'].sum())

    df.to_csv(f'./ablation_results_{output_filename}.csv')


if __name__ == '__main__':
    compare_sql_and_spqral_pred()
