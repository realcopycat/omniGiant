import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
from graph_driver import Neo4jOperator
from dash.dependencies import Input, Output, State


app = dash.Dash(__name__)


flex_style_space_between = {'display': 'flex',
                            'flex-direction': 'row',
                            'justify-content': 'space-between',
                            'align-items': 'center'}


app.layout = html.Div([

    # 标题栏
    html.Nav(className='navbar navbar-expand-lg navbar-dark bg-dark', children=[

        html.Div(className='container', style=flex_style_space_between, children=[
            html.A(className='navbar-brand', style={'color': 'white'}, children=[
                html.Div(children=[
                    "现场勘查知识图谱探索系统",
                    html.Span(className='badge badge-pill badge-warning ml-2', children=["测试版"])
                ]),
            ]),
            html.Button(className='btn btn-outline-success', children=[
                "Contact us"
            ])
        ])
    ]),

    html.Div(className='container', children=[
        # 设置中心
        html.Div(className='row', children=[
            html.Div(className='card-body border my-2 pb-3', children=[
                html.Div(className='container', style=flex_style_space_between, children=[
                    html.Div(className='', style={'flex-basis': '30%', 'flex-grow': '1'}, children=[
                        html.Form(className='', children=[
                            html.Div(className='input-group mb-3', children=[
                                dcc.Input(
                                    className="form-control",
                                    id='search_keyword',
                                    placeholder='Enter a keyword...',
                                    type='text',
                                    value=''
                                ),
                                html.Div(className='input-group-append', children=[
                                    html.Button('开始搜索', id='start_button', type='button',
                                                className="btn btn-info ml-3"),

                                ])
                            ]),
                            html.Div(className='input-group mb-3', children=[
                                dcc.Input(
                                    className="form-control",
                                    id='search_relation_keyword',
                                    placeholder='Enter a relation keyword...',
                                    type='text',
                                    value=''
                                ),
                            ]),
                        ]),
                    ]),

                    html.Div(className='ml-5 mb-5', style={'width': '40%', 'flex-grow': '1'}, children=[
                        html.P("您希望显示的节点个数："),
                        dcc.Slider(
                            id='number_of_main_node',
                            min=0,
                            max=100,
                            step=1,
                            value=10,
                            marks={value: value for x, value in enumerate(range(0, 100, 10))}
                        )
                    ]),
                ])
            ])
        ]),

        html.Div(className='row', children=[
            html.Div(className='col-6', children=[
                dcc.Dropdown(
                    id='layout_select',
                    value='random',
                    clearable=False,
                    options=[
                        {'label': name.capitalize(), 'value': name}
                        for name in ['grid', 'random', 'circle', 'cose', 'concentric']
                    ]
                )
            ])
        ]),

        html.Div(className='row', children=[
            html.Div(className='col-6', children=[
                html.P(id='graph-click-edge-output')
            ])
        ]),

        # 接下来是绘图区域
        html.Div(className='row', children=[
            html.Div(className='col-12', children=[
                cyto.Cytoscape(
                    id='cytoscape-basic',
                    layout={'name': 'cose'},
                    style={'width': '100%', 'height': '1000px'},
                    elements=[],
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)'
                            }
                        },
                        {
                            'selector': '.node',
                            'style': {
                                'background-color': 'blue',
                                'line-color': 'gary'
                            }
                        },
                        {
                            'selector': '.node_main',
                            'style': {
                                'shape': 'rectangle'
                            }
                        }
                    ]
                )
            ])
        ])
    ])
])


# 仅设置搜索框
@app.callback(
    Output('cytoscape-basic', 'elements'),
    [Input('start_button', 'n_clicks'),
     Input('number_of_main_node', 'value')],
    [State('search_keyword', 'value')]
)
def extract_data_from_neo4j(n_clicks, limit, value):
    # 此部分为核心作图数据获取
    driver = Neo4jOperator()  # 初始化数据库驱动
    node_result, link_result = driver.search_data_normal(value, limit)  # 调用驱动提取数据

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


@app.callback(
    Output('graph-click-edge-output', 'children'),
    [Input('cytoscape-basic', 'tapEdgeData')]
)
def display_edge_data(data):
    if data:
        return data['label']
