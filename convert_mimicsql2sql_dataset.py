import sys
sys.path.append('..')
import json
import os

import pandas as pd
from collections import Counter

from mimicsql.evaluation.utils import query
from sql2sql import SQL2SQL


def tokenize_sql(q):
    q = ' . '.join(q.split('.'))
    q = ' , '.join(q.split(','))
    return q.split()


def convert_sql2sparql(filename='train.json', dataset_type='natural', execution=True):
    savedir = f'./dataset/mimicsqlstar/mimicsqlstar_{dataset_type}/'
    datadir = f'./dataset/mimicsql/mimicsql_{dataset_type}/'
    data = []
    with open(os.path.join(datadir, filename)) as json_file:
        for line in json_file:
            data.append(json.loads(line))

    df = pd.DataFrame(data)

    if execution:
        print(f'LOAD original mimic_db ... {len(df)}')
        db_file = './mimicsql/evaluation/mimic_db/mimic.db'
        orimodel = query(db_file)
        print('DONE')

        print('LOAD mimicqlstar.db ...')
        db_file = './build_mimicsqlstar_db/mimicsqlstar.db'
        newmodel = query(db_file)
        print('DONE')

    sql2sql_convertor = SQL2SQL()

    correct = 0
    newsqls = []
    for i, sql in enumerate(df['sql']):
        sql_answer = []
        newsql_answer = []

        print("-" * 50)
        print(i, sql)

        if execution:
            sql_res = orimodel.execute_sql(sql.lower()).fetchall()
            for res in sql_res:
                val = '|'
                temp = []
                for t in res:
                    val += str(t) + '|\t\t|'
                    temp.append(str(t))
                print(val[:-1])
                sql_answer.append(tuple(temp))
        print()

        new_sql = sql2sql_convertor.translate(sql)

        print(i, new_sql)
        if execution:
            newsql_res = newmodel.execute_sql(new_sql.lower()).fetchall()
            for res in newsql_res:
                val = '|'
                temp = []
                for t in res:
                    val += str(t) + '|\t\t|'
                    temp.append(str(t))
                print(val[:-1])
                newsql_answer.append(tuple(temp))

            print(sql_answer, newsql_answer, set(sql_answer) == set(newsql_answer))
            if set(sql_answer) == set(newsql_answer):
                correct += 1
            else:
                print("[incorrect]")
        print()

        new_sql = new_sql.lower()
        newsql_tok = tokenize_sql(new_sql)
        newsqls.append({'sql': new_sql, 'sql_tok': newsql_tok})

    if execution:
        print(f'[SQL2SQL] filenmae: {filename}, Answer Accuracy: {correct/len(df):.4f}')

    sql_data = []
    for d, sql_d in zip(data, newsqls):
        d['sql'] = sql_d['sql']
        d['sql_tok'] = sql_d['sql_tok']
        sql_data.append(d)

    save_filename = os.path.join(savedir, filename)
    with open(save_filename, 'w') as json_file:
        for dic in sql_data:
            json.dump(dic, json_file)
            json_file.write('\n')

    print(f"Write to {save_filename}")


def build_vocab(dataset_type='natural'):
    datadir = f'./dataset/mimicsqlstar/mimicsqlstar_{dataset_type}/'
    filenames = ['train.json']
    counter = Counter()
    for filename in filenames:
        with open(os.path.join(datadir, filename)) as json_file:
            for line in json_file:
                dic = json.loads(line)
                counter.update(dic['question_refine_tok'])
                counter.update(dic['sql_tok'])

    with open(os.path.join(datadir, 'vocab'), 'w') as f:
        for k, v in counter.most_common():

            if len(k.split()) == 0:
                continue

            if k == ' ':
                continue
            f.write(f'{k} {v}\n')

    print(f'vocab builded: {len(counter)}')


if __name__ == '__main__':
    execution = False
    dataset_type = 'natural'
    filenames = ['train.json', 'dev.json', 'test.json']
    for filename in filenames:
        convert_sql2sparql(filename=filename, dataset_type=dataset_type, execution=execution)
    build_vocab(dataset_type=dataset_type)
