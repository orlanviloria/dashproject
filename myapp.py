#https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_More_Advanced_Shit/CRUD_app/crud.py
#https://stackoverflow.com/questions/60223161/using-dash-upload-component-to-upload-csv-file-and-generate-a-graph
import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import csv
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
"graphBackground": "#F5F5F5",
"background": "#ffffff",
"text": "#000000"
}

app.layout = html.Div([
dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=True
),
dcc.Graph(id='Mygraph'),
html.Div(id='output-data-upload'),
html.Button('Export to Excel', id='save_to_csv', n_clicks=0),
 # Create notification when saving to excel
html.Div(id='placeholder', children=[]),
dcc.Store(id="store", data=0),
dcc.Interval(id='interval', interval=1000)
])

#Graph

@app.callback(Output('Mygraph', 'figure'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def update_graph(contents, filename):
    x = []
    y = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        x=df['DATE']
        y=df['Sales']
        #print(df)
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x, 
                y=y, 
                mode='lines+markers')
            ],
        layout=go.Layout(
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"]
        ))
    return fig



def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(Output('output-data-upload', 'children'),
          [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def update_table(contents, filename):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        da=df.to_dict('rows')
        print(da)
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                editable=True
            ),
    
            # html.Hr(),
            # html.Div('Raw Content'),
            # html.Pre(contents[0:200] + '...', style={
            #     'whiteSpace': 'pre-wrap',
            #     'wordBreak': 'break-all'
            # }),
        #print(table)
        ])

    return table

########################################## Save to CSV
def update_tabl(contents, filename):

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)

        dff = dash_table.DataTable(data=df.to_dict('rows'), columns= [{'name': i, 'id': i} for i in df.columns],
                        editable=True
            ),
        print(dff)
            

    return dff

@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_csv', 'n_clicks'),
     Input("interval", "n_intervals")],
    [
     State('store', 'data'),
     State('upload-data', 'contents'),State('upload-data', 'filename')]
)
def df_to_csv(n_clicks, n_intervals, s,contents,filename):
    output = html.Plaintext("The data has been saved to your folder.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_triggered == "save_to_csv":
        s = 6
        df=update_tabl(contents,filename)
        
        df=pd.DataFrame(df)
        print(df)
        df.to_csv("Your_Sales_Data.csv")
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s-1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s




if __name__ == '__main__':
    app.run_server(debug=True,host = '127.0.0.1') 
