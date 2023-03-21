import os
import requests
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
# Use environment variables to store API keys
API_KEY = os.environ.get('ADZUNA_API_KEY')
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')

def fetch_job_data(query, country_code='ca', results_per_page=20, page=1):
    base_url = 'https://api.adzuna.com/v1/api/jobs'
    url = f'{base_url}/{country_code}/search/{page}?app_id={ADZUNA_APP_ID}&app_key={API_KEY}&results_per_page={results_per_page}&what={query}&content-type=application/json'
    print(url)
    response = requests.get(url)
    data = response.json()
    if 'results' in data:
        return data['results']
    else:
        return []  # Return an empty list if 'results' key doesn't exist


def process_job_data(job_data):
    jobs_df = pd.DataFrame(job_data)
    return jobs_df

def create_pie_chart(df, col):
    fig = px.pie(df, names=col, title=f'Distribution of {col}')
    return fig

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP]) # type: ignore

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Job Skills Dashboard"), className="text-center")
    ], className="mt-5"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="filter-job-title",
                options=[
                    {'label': 'Data Scientist', 'value': 'data scientist'},
                    {'label': 'Data Analyst', 'value': 'data analyst'},
                    {'label': 'Statistician', 'value': 'statistician'}
                ],
                value='data scientist'
            )
        ])
    ], className="mt-3"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="job-title-pie-chart")
        ])
    ], className="mt-3")
])

@app.callback(
    Output("job-title-pie-chart", "figure"),
    [Input("filter-job-title", "value")],
)
def update_pie_chart(job_title):
    job_data = fetch_job_data(job_title)
    jobs_df = process_job_data(job_data)
    pie_chart = create_pie_chart(jobs_df, 'category')
    return pie_chart

if __name__ == '__main__':
    app.run_server(debug=True)
