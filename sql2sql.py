import json
import os
import re
import numpy as np
import pandas as pd
import networkx as nx
from build_mimicsqlstar_db.schema_mimic import SCHEMA, MAP_WITH_MIMICSQL
from collections import OrderedDict
from itertools import repeat


class SQL2SQL:
    def __init__(self):
        self.schema_graph = nx.Graph()
        for k, vs in SCHEMA.items():
            for v in vs:
                self.schema_graph.add_edge(k, v[0])
        self.inner_join_template = 'INNER JOIN {} ON {} = {}'

    def find_table(self, block):
        cols = re.findall('[A-Z_]+[.]"[\dA-Z_]+"', block)
        return [c.split('.')[0] for c in cols]

    def from_caluse(self, new_select):
        cols = re.findall('[A-Z_]+[.]"[\dA-Z_]+"', new_select)
        for col in cols:
            t, c = col.split('.')
            return t

    def cols_clause(self, block):
        cols = re.findall('[A-Z_]+[.]"[\dA-Z_]+"', block)
        #print(cols)
        for col in cols:
            t, c = col.split('.')
            new_tc = MAP_WITH_MIMICSQL[t][c.replace('"', '')]
            #print(new_tc)
            block = block.replace(col, new_tc)
            # print(col, new_tc)
        return block

    def translate(self, sql):
        remain, where_block = sql.split('WHERE')
        select_block, remain = remain.split('FROM')

        new_select = self.cols_clause(select_block)
        select_tables = self.find_table(new_select)
        from_table = self.from_caluse(new_select)
        new_where = self.cols_clause(where_block)
        where_tables = self.find_table(new_where)
        # print(new_select)
        # print(from_table)
        # print(new_where)
        # print(where_tables)
        inner_join_blocks = list()
        tables = list(set(where_tables + select_tables))
        for wt in tables:
            path = nx.shortest_path(self.schema_graph, source=from_table.replace(' ', ''), target=wt.replace(' ', ''))
            for i in range(len(path) - 1):
                a = path[i]
                b = path[i+1]
                key = [con[1] for con in SCHEMA[a] if con[0] == b][0]
                inner_join_block = self.inner_join_template.format(b, f'{a}."{key}"', f'{b}."{key}"')
                #print(inner_join_block)
                inner_join_blocks.append(inner_join_block)

        inner_join_blocks = list(OrderedDict(zip(inner_join_blocks, repeat(None))))
        new_inner_join = ' '.join(list(inner_join_blocks))
        #print(new_inner_join)

        temp = 'FROM '.join([new_select, from_table])
        temp = ' '.join([temp, new_inner_join])
        temp = ' '.join(temp.split(' ')) + ' '
        new_sql = 'WHERE'.join([temp, new_where])
        return new_sql


if __name__ == '__main__':
    convertor = SQL2SQL()
    sql = 'SELECT DEMOGRAPHIC."GENDER",DEMOGRAPHIC."INSURANCE" FROM DEMOGRAPHIC WHERE DEMOGRAPHIC."SUBJECT_ID" = "81923"'
    new_sql = convertor.translate(sql)
    print(sql)
    print(new_sql)
