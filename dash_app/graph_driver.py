from neo4j import GraphDatabase
import os


class Neo4jOperator:

    def __init__(self):
        password = os.getenv("NEO_PW")  # 运行前注意设置环境变量
        username = os.getenv("NEO_NAME") or 'neo4j'
        self._driver = GraphDatabase.driver("bolt://localhost:7687", auth=(username, password))

    def search_data_normal(self, node_name):
        """
        普通的节点搜索模式
        :param node_name: 节点名称
        :return: 节点列表, edge列表
        """
        with self._driver.session() as session:
            result = \
                session.run(
                    "match (a:node_main {name: $node_name})-[b]->c return a,b,c",
                    node_name=node_name
                )

            edge_result_list_dict = list()  # 其格式主要参照dash-cytoscape的文档要求 注意查阅https://dash.plot.ly/cytoscape/elements
            node_result_list_dict = list()
            main_node_set = set()  # 为了区分主node与普通node
            not_main_node_set = set()

            for each_record in result:  # 对结果进行解析
                main_node_set.add(each_record['a.name'])
                not_main_node_set.add(each_record['b.name'])

                edge_result_list_dict.append({
                    'source': each_record['a.name'],
                    'target': each_record['c.name'],
                    'edge': each_record['c.description']  # 边的内容
                })

            real_not_main_node_list = not_main_node_set - (not_main_node_set & main_node_set)  # 考虑到有些节点可能既是一般节点也是主节点 就先取交集然后减掉，得到真正的一般节点集合

            node_result_list_dict.extend([{
                'category': 'main_node',
                'label': x
            }] for x in main_node_set)  # 制作节点列表1

            node_result_list_dict.extend([{
                'category': 'node',
                'label': x
            }] for x in real_not_main_node_list)  # 制作节点列表2

        return node_result_list_dict, edge_result_list_dict
