from neo4j import GraphDatabase
import os


class Neo4jOperator:

    def __init__(self):
        password = os.getenv("NEO_PW")  # 运行前注意设置环境变量
        username = os.getenv("NEO_NAME") or 'neo4j'
        self._driver = GraphDatabase.driver("bolt://localhost:7687", auth=(username, password))

    def search_data_normal(self, node_name, number_limit=50):
        """
        普通的节点搜索模式
        :param number_limit: 限制结果数量
        :param node_name: 节点名称
        :return: 节点列表, edge列表
        """
        with self._driver.session() as session:
            result = \
                session.run(
                    "MATCH p = (a)-[*..5]->(c)"  # 注意参考cypher语法
                    "WHERE a.name CONTAINS $node_name "
                    "RETURN *, relationships(p) LIMIT $limit",
                    node_name=node_name, limit=number_limit
                )

            edge_result_list_dict = list()  # 其格式主要参照dash-cytoscape的文档要求 注意查阅 https://dash.plot.ly/cytoscape/elements
            node_result_list_dict = list()
            node_set = set()  # 用于避免反复录入

            for each in result.records():
                # 每一个each都是一个路径，接下来要对这个路径做解析
                for x in list(each['p'].graph.relationships._entity_dict.items()):  # 这里涉及到了对于内部成员的访问，但是没有办法，这样是比较方便的方法
                    tmp_relation_description = x[1]._properties['description']  # 这个x[1]是因为x[0]是该路径的id，这里list的每一元素都是一个元组
                    tmp_start_node = x[1].start_node._properties[
                        'name']  # 具体的访问实现细节请结合debug功能以及https://neo4j.com/docs/api/python-driver/1.7/results.html
                    tmp_start_node_category = list(x[1].start_node.labels)  # list of str
                    tmp_start_node_id = x[1].start_node._id
                    tmp_end_node = x[1].end_node._properties['name']
                    tmp_end_node_category = list(x[1].end_node.labels)  # list of str
                    tmp_end_node_id = x[1].end_node._id

                    # 制作结果数据 通过下述的语句，将路径中的节点和关系分解为一个一个的节点以及节点之间的关系
                    # 为接下来的数据读取做好准备。其格式主要是为了dash的elements属性作准备
                    if tmp_start_node_id not in node_set:
                        node_set.add(tmp_start_node_id)
                        node_result_list_dict.append({
                            'id': tmp_start_node_id,
                            'label': tmp_start_node,
                            'category': tmp_start_node_category
                        })
                    if tmp_end_node_id not in node_set:
                        node_set.add(tmp_end_node_id)
                        node_result_list_dict.append({
                            'id': tmp_end_node_id,
                            'label': tmp_end_node,
                            'category': tmp_end_node_category
                        })

                    edge_result_list_dict.append({
                        'source': tmp_start_node_id,
                        'target': tmp_end_node_id,
                        'edge_description': tmp_relation_description
                    })

        return node_result_list_dict, edge_result_list_dict

    @staticmethod
    def data_packing(node_result, link_result):
        nodes = list()
        for _, node_dict in enumerate(node_result):
            tmp_node = {
                'data': {'id': node_dict['id'], 'label': node_dict['label']},
                'classes': ' '.join(node_dict['category'])  # 这里是把列表内的字符串拼接在一起，这样可以满足dash的要求
                # 具体参见 https://dash.plot.ly/cytoscape/styling
            }
            nodes.append(tmp_node)  # 之所以要用与下面的不一样的方法，是因为这里用到的enumerate是一个迭代器。并非一个完整的list

        # edges = list()
        edges = [
            {
                'data': {'source': link_dict['source'],
                         'target': link_dict['target'],
                         'label': link_dict['edge_description']
                         }
            }
            for link_dict in link_result
        ]

        elements = nodes + edges

        return elements
