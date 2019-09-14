import dash
import dash_cytoscape as cyto
import dash_core_components as dcc
import dash_html_components as html
from graph_driver import Neo4jOperator

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(className='container', children=[

        # 设置中心
        html.Div(className='row', children=[
           html.Div(className='col-4', children=[
               dcc.Slider(
                   id='number_of_main_node',
                   min=3,
                   max=100,
                   step=1,
                   value=10,
                   marks={x: value for x, value in enumerate(range(3, 100, 5))}
               )
           ]),
           html.Div(className='col-4', children=[
              dcc.Input(
                  placeholder='Enter a keyword...',
                  type='text',
                  value=''
              ),
              html.Button('开始搜索', id='start_button')
           ]),
        ]),

        # 接下来是绘图区域
        html.Div(className='row', children=[
            html.Div(className='col-12', children=[
                cyto.Cytoscape(
                    id='cytoscape-basic',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '400px'},
                    elements=[

                    ]
                )
            ])
        ])
    ])
])
