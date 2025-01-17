import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
from graph_driver import Neo4jOperator
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

flex_style_space_between = {  # 通用的flex布局style
    'display': 'flex',
    'flex-direction': 'row',
    'justify-content': 'space-between',
    'align-items': 'center'
}

cover_css = {  # 用于布局这个封面的css文件
    "height": "60rem",
    "background-position": "0% 0%",
    "background-size": "cover",
    "background-image": 'url("/assets/img/bg1.jpg")'
}

app.layout = html.Div(style={'height': '100%'}, children=[

    # 标题栏
    html.Nav(className='navbar navbar-expand-lg navbar-dark bg-dark', children=[

        html.Div(className='container', style=flex_style_space_between, children=[
            html.A(className='navbar-brand', style={'color': 'white'}, children=[
                html.Div(children=[
                    "OMNI知识图谱探索系统",
                    html.Span(className='badge badge-pill badge-warning ml-2', children=["测试版"])
                ]),
            ]),
            html.Button(className='btn btn-outline-success', children=[
                "Contact us"
            ])
        ])
    ]),

    # 应用封面
    html.Div(className="jumbotron jumbotron-fluid text-center", id="cover", style=cover_css, children=[
        html.H1(style={"letter-spacing": "1.5rem", "color": "white", "height": "6rem", "font-size": "400%"}, children=[
            "OMNI知识图谱探索系统"
        ]),
        html.P(style={"height": "5rem", "letter-spacing": "0.2rem", "color": "white"}, children=[
            "OMNI Knowledge Graph Exploring System"
        ]),
        html.H3(style={"height": "4rem", "color": "white"}, children=[
            html.Em(children=[
                "The truth is more important than the facts."
            ])
        ]),
        html.H3(style={"height": "4rem", "color": "white"}, children=[
            html.Em(children=[
                "——  Frank Lloyd Wright"
            ])
        ]),
        html.P(style={"margin-top": "6rem"}, children=[
            html.Button(className="btn btn-secondary", id="uncover_button", role="button", children=[
                "即刻使用"
            ])
        ])
    ]),

    html.Div(className='container-fluid', style={'background-color': '#3A4D4C', 'height': '100%'}, children=[
        html.Div(className='row', children=[
            html.Div(className='col-3 d-xs-none', children=[
                html.Ul(className='nav nav-tabs nav-stacked border-0', children=[
                    html.Div(className='d-flex flex-column justify-content-start w-100', children=[
                        html.Div(className='flex-fill', children=[
                            html.Div(className='d-flex flex-column justify-content-start my-4 border px-3 py-3',
                                     style={'background-color': '#425257'},
                                     children=[
                                         html.Strong(className='my-3', children=[
                                             "知识节点查询"
                                         ]),
                                         dcc.Input(className="form-control mb-4 flex-fill",
                                                   id='search_keyword',
                                                   placeholder='Enter a keyword...',
                                                   type='text',
                                                   value='氰'
                                                   ),
                                         html.Button('开始搜索',
                                                     id='main_search_button',
                                                     type='button',
                                                     className="btn btn-primary btn-block mb-4",
                                                     n_clicks_timestamp=0,
                                                     ),
                                         html.P(className='mb-4', children=["您希望显示的节点个数："]),
                                         dcc.Slider(id='number_of_main_node',
                                                    className='mb-4 ml-3',
                                                    min=0,
                                                    max=100,
                                                    step=1,
                                                    value=10,
                                                    marks={
                                                        value: value for x, value in enumerate(range(0, 100, 10))
                                                    }),
                                         html.Button('清空',
                                                     id='clear_graph',
                                                     type='button',
                                                     className="btn btn-warning btn-block my-3",
                                                     n_clicks_timestamp=0)
                                     ])
                        ]),
                        html.Li(children=[
                            html.Div(className='d-flex flex-column justify-content-start mb-4 border px-3 py-3',
                                     style={'background-color': '#425257'},
                                     children=[
                                         html.Strong(className='my-3', children=[
                                             "知识节点筛选"
                                         ]),
                                         html.Div(className='input-group mb-3', children=[
                                             dcc.Input(className="form-control",
                                                       id='search_relation_keyword',
                                                       placeholder='Enter a relation keyword...',
                                                       type='text',
                                                       value=''
                                                       )
                                         ]),
                                         html.Button('筛选',
                                                     id='filter_button',
                                                     type='button',
                                                     className="btn btn-primary btn-block mb-4",
                                                     n_clicks_timestamp=0
                                                     ),
                                         html.Strong(className='my-3', children=[
                                             "节点布局调节"
                                         ]),

                                         dcc.Dropdown(id='layout_select',
                                                      value='random',
                                                      clearable=False,
                                                      options=[
                                                          {'label': name.capitalize(), 'value': name}
                                                          for name in
                                                          ['grid', 'random', 'circle', 'cose',
                                                           'concentric']
                                                      ])
                                     ]),
                        ])
                    ])
                ]),
            ]),
            html.Div(className='col-9', children=[
                # 接下来是绘图区域
                html.Div(className='card my-3', style={'background-color': '#424757'}, children=[
                    html.Div(className='card-body border', children=[
                        html.Div(id='for_alert', children=[]),
                        cyto.Cytoscape(
                            id='cytoscape-basic',
                            layout={'name': 'cose'},
                            style={'width': '100%', 'height': '600px'},
                            elements=[],
                            stylesheet=[  # 此处为绘图style 控制
                                {
                                    'selector': 'node',
                                    'style': {
                                        'content': 'data(label)'
                                    }
                                },
                                {
                                    'selector': '.node',
                                    'style': {
                                        'background-color': '#FFEFC2',
                                        'line-color': '#A8BBFF',
                                        'color': 'white'
                                    }
                                },
                                {
                                    'selector': '.node_main',
                                    'style': {
                                        'shape': 'rectangle',
                                        'background-color': '#FFE18F'
                                    }
                                },
                                {
                                    'selector': '.edge',
                                    'style': {
                                        'line-color': '#15171C'
                                    }
                                }
                            ]
                        )
                    ])
                ]),
                html.Div(className='', children=[
                    html.Div(className='card w-auto h-50 border', style={'background-color': '#3B3A4D'}, children=[
                        html.Div(className='card-body', children=[
                            html.Div(className='', children=[
                                html.Div(className='mb-3', children=[
                                    html.Strong(style={'color': 'white'}, children=["关系内容（选中后更新）："]),
                                ]),
                                html.Div(className='mx-auto', children=[
                                    html.P(style={'color': 'white'}, id='graph-click-edge-output')
                                ]),
                            ]),
                        ])
                    ]),
                ]),
            ])
        ]),
    ]),
])


def alert_response(boolean_result):
    if boolean_result:  # 如为真 则是有结果
        string_for_alert = '已更新图谱'
    else:
        string_for_alert = '未查找到相关数据'
    response = html.Div(className='alert alert-warning alert-dismissible fade show', role="alert", children=[
        html.P(children=[string_for_alert]),
        html.Button(type='button', className='close',
                    **{
                        'data-dismiss': 'alert',
                        'aria-label': 'Close'
                    },
                    children=[
                        html.Span(**{'aria-hidden': 'true'}, children=[
                            '&times;'
                        ])

                    ])
    ])
    return response


# 仅设置搜索框
@app.callback(
    Output('cytoscape-basic', 'elements'),
    [Input('main_search_button', 'n_clicks_timestamp'),
     Input('number_of_main_node', 'value'),
     Input('filter_button', 'n_clicks_timestamp'),
     Input('clear_graph', 'n_clicks_timestamp'),
     Input('cytoscape-basic', 'tapNodeData')],
    [State('search_keyword', 'value'),
     State('search_relation_keyword', 'value'),
     State('cytoscape-basic', 'elements')]
)
def extract_data_from_neo4j(n_clicks, limit, n_clicks_of_relation, n_clicks_of_clear,
                            tap_node_data, value, value_relation, origin_element_data):
    # 此部分为核心作图数据获取

    driver = Neo4jOperator()  # 初始化数据库驱动
    node_result, link_result = driver.search_data_normal(value, limit)  # 调用驱动提取数据

    elements = driver.data_packing(node_result, link_result)  # 调用封装好的静态方法

    # 数据节点选中并刷新
    if tap_node_data:
        new_node, new_link = driver.search_data_normal(tap_node_data['label'])
        new_element = driver.data_packing(new_node, new_link)
        elements = origin_element_data + new_element  # 叠加数据

    # 接下来是筛选器
    if value_relation == '':
        filter_data = elements
    else:
        filter_data = []
        for each in elements:
            try:
                _ = each['data']['source']  # 用于测试是否是节点数据
                # target_node = each['data']['target']
            except KeyError as _:
                # 如果进入此处说明是个节点数据,直接接入
                filter_data.append(each)
                continue
            else:
                if value_relation in each['data']['label']:
                    filter_data.append(each)
                else:
                    continue

    if int(n_clicks_of_clear) > int(n_clicks_of_relation) and \
            int(n_clicks_of_clear) > int(n_clicks):
        filter_data = []

    return filter_data


# 得到边的信息
@app.callback(
    Output('graph-click-edge-output', 'children'),
    [Input('cytoscape-basic', 'tapEdgeData')]
)
def display_edge_data(data):
    if data:
        return data['label']


@app.callback(
    Output('cover', 'className'),
    [Input('uncover_button', 'n_clicks')]
)
def uncover(n_clicks):
    if n_clicks is None or n_clicks <= 0:
        return "jumbotron jumbotron-fluid text-center"
    return "d-none"


@app.callback(
    Output('cytoscape-basic', 'layout'),
    [Input('layout_select', 'value')]
)
def layout_setting(layout):
    return {'name': layout}
