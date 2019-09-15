import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
from graph_driver import Neo4jOperator
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(className='container', children=[

        # 设置中心
        html.Div(className='row', children=[
           html.Div(className='col-6', children=[
               dcc.Slider(
                   id='number_of_main_node',
                   min=3,
                   max=100,
                   step=1,
                   value=10,
                   marks={value: value for x, value in enumerate(range(1, 100, 10))}
               )
           ]),

           html.Div(className='col-6', children=[
              dcc.Input(
                  id='search_keyword',
                  placeholder='Enter a keyword...',
                  type='text',
                  value=''
              ),

              html.Button('开始搜索', id='start_button')
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
           ])
        ]),

        # 接下来是绘图区域
        html.Div(className='row', children=[
            html.Div(className='col-12', children=[
                cyto.Cytoscape(
                    id='cytoscape-basic',
                    layout={'name': 'cose'},
                    style={'width': '100%', 'height': '1000px'},
                    elements=[

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
     Input('layout_select', 'value')],
    [State('search_keyword', 'value')]
)
def extract_data_from_neo4j(n_clicks, layout, value):

    # 此部分为核心作图数据获取
    driver = Neo4jOperator()  # 初始化数据库驱动
    node_result, link_result = driver.search_data_normal(value)  # 调用驱动提取数据

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
                     'label': link_dict['edge']
                     }
        }
        for link_dict in link_result
    ]
    elements = nodes + edges

    return elements