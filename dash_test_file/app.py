import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# external_stylesheets = ["bootstrap.css"]

df = pd.read_csv(
    "./dataset/gapminderDataFiveYear.csv"
)

app = dash.Dash(__name__)

all_option = {
    'America': ['NewYork', 'Cincinnati'],
    'Canada': ['Toronto', 'Ottawa']
}

app.layout = html.Div(children=[
    html.H1(children='Hello World'),

    html.Div(className='container', children=[
        html.Div(className="row", children=[
            html.Div(className='col-md-4 col-lg-4', children=[
                dcc.RadioItems(
                    id='conuntries-dropdown',
                    options=[{'label': k, 'value': k} for k in all_option.keys()],
                    value='America'
                ),
                html.Hr(),  # 分割线类似物

                dcc.RadioItems(id='cities-dropdown'),

                html.Hr(),

                html.Div(id='display-selected-values')
            ]),

            html.Div(className='col-md-4 col-lg-4', children=[
                dcc.Input(id='my-id', value='initial', type='text')
            ]),

            html.Div(className='col-md-4 col-lg-4', children=[
                html.Div(id='my-div')
            ])
        ])
    ]),

    html.Div(className='container', children=[
        dcc.Graph(id='graph'),  # graph对象就是用来作图的
        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),  # 此处是pandas的用法 注意借鉴
            max=df['year'].max(),
            value=df['year'].min(),
            marks={str(year): str(year) for year in df['year'].unique()},  # 这个unique大概是多个存在值选择一个
            step=None
        )
    ]),

    html.Div
])


@app.callback(
    Output('cities-dropdown', 'options'),
    [Input('countries-dropdown', 'value')]
)
def set_cities_options(selected_country):  # 这个input的顺序就是参数的顺序，而return的值就是这个output的属性
    return [{'label': i, 'value': i} for i in all_option[selected_country]]


@app.callback(
    Output('cities-dropdown', 'value'),
    [Input('countries-dropdown', 'options')]
)
def set_cities_value(available_options):
    return available_options[0]['value']



@app.callback(
    Output('graph', 'figure'),  # 前面一个参数是id， 后面一个参数是该id内的属性 figure就是设置图像的属性
    [Input('year-slider', 'value')]
)
def update_figure(select_year):
    filtered_df = df[df.year == select_year]  # 列表的遍历并选择！！！高级用法！！！
    traces = []
    for i in filtered_df.continent.unique():  # 筛选出相关年份之后 对于每一个洲再做细分
        df_by_continent = filtered_df[filtered_df['continent'] == i]  # 同上，对列表数据的遍历并选择
        traces.append(go.Scatter(  # 这里用到了plotly组件
            x=df_by_continent['gdpPercap'],  #
            y=df_by_continent['lifeExp'],
            text=df_by_continent['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'GDP Per Capita'},
            yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=True)
