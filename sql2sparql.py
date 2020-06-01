import re
import networkx as nx
from build_mimicsparql_kg.kg_schema import SCHEMA_DTYPE, KG_SCHEMA
from collections import OrderedDict
from itertools import repeat

def cond_syntax_fix(sparql):
    match = re.findall('"?[^>]*"?\^\^', sparql)
    for m in match:
        sparql = sparql.replace(m, ' "' + m.split('^^')[0].strip().replace('"', '') + '"^^')
    return sparql

# entity 공백을 준다.
def split_entity(sparql):
    match = re.findall('</[a-z_]+/[\d.]+>',sparql)
    for m in match:
        val = re.findall('[\d.]+',m)[0]

        f, a = re.sub(val,' ', m).split()
        repla = ' '.join([f, val, a])
        sparql = re.sub(m, repla, sparql)
    return sparql

# entity 공백을 다시 채운다.
def join_entity(sparql):
    match = re.findall('</[a-z_]+/ [\d\.]+ >[\. ]', sparql)
    for m in match:
        sparql = re.sub(m, ''.join(m.split() + [' ']), sparql)
    return sparql

def clean_text(val):
    if type(val) == str:
        val = val.replace("\\", ' ')
    return val

def sparql_postprocessing(sparql):
    sparql = clean_text(sparql.lower()) # sparql 소문자이나 한번더 소문자로 바꿔놓음
    sparql = sparql.replace('/xmlschema#', '/XMLSchema#') # 소문자라서 스키마 일치가 안되는 경우
    sparql = sparql.replace(' ^^<http://www', '^^<http://www') # ^^와 condition이 떨어져 있는 경우
    sparql = sparql.replace(' <stop>', '') # prediction의 <stop> 토큰 제거
    sparql = cond_syntax_fix(sparql) # condition "val"^^ syntax error fix
    return sparql


class SQL2SPARQL:
    def __init__(self):
        self.schema_graph = nx.DiGraph()
        for k, vs in KG_SCHEMA.items():
            for v in vs:
                self.schema_graph.add_edge(k.lower(), v.lower())
        self.agg_func = ['count', 'max', 'min', 'avg']
        self.sel_p = re.compile('"[^"]*"')
        self.cond_p = re.compile('"[^"]*"|[=><]+')
        self.sparql_agg_template = "select ( {AGG} ( {DISTINCT} ?{COL} ) as ?agg ) "
        self.sparql_select_template = "select"
        self.root = 'subject_id'
        self.schema_type = {k.lower(): v for k, v in SCHEMA_DTYPE.items()}
        self.duplicate_columns = ['short_title', 'long_title', 'icd9_code']

    def _replace_dulicate_column(self, sql):
        for col in self.duplicate_columns:
            tokens = [token.split('.') for token in re.findall(f'[a-z]+."{col}"', sql)]
            for table, _ in tokens:
                sql = re.sub(f'{table}."{col}"', f'"{table}_{col}"', sql)
        return sql

    def get_max_hop(self, sql):
        sql = self._replace_dulicate_column(sql)
        remain, where_part = sql.split(' where ')
        select_part, remain = remain.split(' from ')

        distinct_term = 'distinct' if 'distinct' in select_part else ''
        agg_f = self._get_agg_func(select_part)
        select_cols = self._get_select_col(select_part)
        select_term = self._make_select_term(select_cols, agg_f, distinct_term)

        conds = self._get_conds(where_part)
        triples, max_length = self._get_sparql_where_triples(select_cols, conds)
        return max_length

    def convert(self, sql):
        sql = self._replace_dulicate_column(sql)
        sparql = self._parse_sql(sql)
        return sparql

    def _parse_sql(self, sql):
        remain, where_part = sql.split(' where ')
        select_part, remain = remain.split(' from ')

        distinct_term = 'distinct' if 'distinct' in select_part else ''
        agg_f = self._get_agg_func(select_part)
        select_cols = self._get_select_col(select_part)
        select_term = self._make_select_term(select_cols, agg_f, distinct_term)

        conds = self._get_conds(where_part)
        where_term = self._make_where_term(select_cols, conds)
        sql = f'{select_term} {where_term}'
        return sql

    def _get_agg_func(self, select_part):
        for f in self.agg_func:
            if f in select_part.split():
                return f
        return None

    def _get_select_col(self, select_part):
        return [col.replace('"', '') for col in re.findall(self.sel_p, select_part)]

    def _get_conds(self, where_part):
        tokens = re.findall(self.cond_p, where_part)
        assert len(tokens) % 3 == 0
        conds = [[tokens[i].replace('"', '')] + tokens[i+1:i+3] for i in range(0, len(tokens), 3)]
        return conds

    def _make_select_term(self, select_cols, agg_f, distinct):
        term = self.sparql_select_template
        if agg_f:
            term = self.sparql_agg_template.format(AGG=agg_f, DISTINCT=distinct, COL=select_cols[0].lower())
            return term

        for col in select_cols:
            term += f' ?{col.lower()}'

        return term

    def _make_where_term(self, sel_cols, conds):
        triples, max_length = self._get_sparql_where_triples(sel_cols, conds)
        term = f'where {{ {". ".join(triples)}. }}'
        return term

    def _path2triples(self, path):
        path.reverse()
        t = [f"?{path.pop().lower()}"]
        triples = []
        while len(path) > 0:
            if len(t) == 0:
                t.append(f"?{path[-1].lower()}")
                path.pop()
            elif len(t) == 1:
                t.append(f"</{path[-1]}>")
            elif len(t) == 2:
                t.append(f"?{path[-1].lower()}")
            elif len(t) == 3:
                triples.append(t)
                t = []
            else:
                print('error')
        return triples

    def _get_sparql_where_triples(self, sel_cols, conds):
        max_length = 0
        triples = []
        filters = []
        for sel_col in sel_cols:
            for cond_col, op, val in conds:
                root2sel = nx.shortest_path(self.schema_graph, source=self.root, target=sel_col)
                sel_triples = self._path2triples(root2sel)

                root2con = nx.shortest_path(self.schema_graph, source=self.root, target=cond_col)
                if max_length < len(root2con):
                    max_length = len(root2con)

                if max_length < len(root2sel):
                    max_length = len(root2sel)

                if len(root2con) > 1:
                    con_triples = self._path2triples(root2con)
                    if op == '=':
                        con_triples = [self._fill_cond_value(t, cond_col, val) for t in con_triples]
                    else:
                        filters.append(f"""filter( ?{cond_col.lower()} {op} {val.replace('"', '')} )""")
                    a = [' '.join(t) for t in sel_triples]
                    b = [' '.join(t) for t in con_triples]

                else:
                    if op == '=':
                        sel_triples = [self._fill_cond_value(t, cond_col, val) for t in sel_triples]
                    else:
                        raise Exception()
                    a = [' '.join(t) for t in sel_triples]
                    b = []

                b = [t for t in b if b not in a]

                triples += list(OrderedDict(zip(a + b, repeat(None))))

        return list(OrderedDict(zip(triples, repeat(None)))) + filters, max_length

    def _fill_cond_value(self, t, cond_col, val):
        sub = t[0]
        rel = t[1]
        cond = t[2]

        if cond.replace('?', '') == cond_col:
            cond_name = cond.replace('?', '')
            if self.schema_type[cond_name] == 'entity':
                cond = f"""</{cond_name}/{val.replace('"', '')}>"""
            else:
                cond = f'{val}^^<{self.schema_type[cond_name]}>'

        elif sub.replace('?', '') == cond_col:
            sub_name = sub.replace('?', '')
            if self.schema_type[sub_name] == 'entity':
                sub = f"""</{sub_name}/{val.replace('"', '')}>"""
            else:
                raise Exception()

        return sub, rel, cond


if __name__ == '__main__':
    sql2sparql = SQL2SPARQL()

    sql = """SELECT MIN ( ADMISSIONS."AGE" ) 
                FROM ADMISSIONS
                WHERE ADMISSIONS."DIAGNOSIS" = "S/P FALL" AND ADMISSIONS."ADMITYEAR" >= "2119"
            """
    # remain, where_part = sql.split(' WHERE ')
    # select_part, remain = remain.split(' FROM ')

    sql = sql2sparql._replace_dulicate_column(sql)
    print(sql)
    result_sparql = sql2sparql._parse_sql(sql)
    print(result_sparql)