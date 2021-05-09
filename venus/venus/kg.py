#!/usr/bin /python38
from py2neo import Graph, Node
from py2neo.data import Relationship
from venus.stock_base import StockEventBase
from libmysql_utils.mysql8 import GLOBAL_HEADER
import re

graph = Graph('http://localhost:7474', username='neo4j', password='neutrino2020')


def create_stock_node():
    event = StockEventBase(GLOBAL_HEADER)
    df = event.mysql.select_values('stock_manager', 'stock_code,stock_name')
    df.columns = ['stock_code', 'stock_name']
    graph = Graph('http://localhost:7474', username='neo4j', password='neutrino2020')
    tx = graph.begin()
    for index, row in df.iterrows():
        # print(f"{row['stock_code']}:{row['stock_name']}")
        tx.create(Node('stock', stock_code=row['stock_code'], name=row['stock_name']))
    tx.commit()


def create_gics_node(graph: Graph):
    event = StockEventBase(GLOBAL_HEADER)
    df = event.mysql.select_values('gics', 'code,name,level')
    df.columns = ['code', 'name', 'level']
    sector = df[df['level'] == 0]
    industry_group = df[df['level'] == 1]
    industry = df[df['level'] == 2]
    sub_industry = df[df['level'] == 3]
    t = graph.begin()
    label0 = ('gics', 'Sector')
    for index, node in sector.iterrows():
        t.create(Node(*label0, code=node['code'], name=node['name'])) 
    label1 = ('gics', 'Industry_Group')
    for index, node in industry_group.iterrows():
        t.create(Node(*label1, code=node['code'], name=node['name']))
    label2 = ('gics', 'Industry')
    for index, node in industry.iterrows():
        t.create(Node(*label2, code=node['code'], name=node['name']))
    label3 = ('gics', 'Sub_Industry')
    for index, node in sub_industry.iterrows():
        t.create(Node(*label3, code=node['code'], name=node['name']))
    t.commit()


def create_relationship_in_gics_node(graph: Graph):

    t = graph.begin()
    n0 = graph.nodes.match("gics", "Sector")
    n0_list = list(n0)
    n1 = graph.nodes.match("gics", "Industry_Group")
    n1_list = list(n1)
    n2 = graph.nodes.match("gics", "Industry")
    n2_list = list(n2)
    n3 = graph.nodes.match("gics", "Sub_Industry")
    n3_list = list(n3)
    for nx in n0_list:
        for ny in n1_list:
            if re.match(nx['code'], ny['code']):
                t.create(Relationship(nx, 'sub_class', ny))
    for nx in n1_list:
        for ny in n2_list:
            if re.match(nx['code'], ny['code']):
                t.create(Relationship(nx, 'sub_class', ny))
    for nx in n2_list:
        for ny in n3_list:
            if re.match(nx['code'], ny['code']):
                t.create(Relationship(nx, 'sub_class', ny))
    t.commit()


def test(graph: Graph):
    tx = graph.begin()
    tx.create(Node('test'))
    tx.commit()


if __name__ == "__main__":
    # create_gics_node(graph)
    # create_relationship_in_gics_node(graph)
