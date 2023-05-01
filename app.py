import os
import requests
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from flask import Flask
from dotenv import load_dotenv
import re


load_dotenv()
# Use environment variables to store API keys
API_KEY = os.environ.get("ADZUNA_API_KEY")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")


def fetch_job_data(query, country_code="ca", results_per_page=20, page=1):
    base_url = "https://api.adzuna.com/v1/api/jobs"
    url = f"{base_url}/{country_code}/search/{page}?app_id={ADZUNA_APP_ID}&app_key={API_KEY}&results_per_page={results_per_page}&what={query}&content-type=application/json"
    print(url)
    response = requests.get(url)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        return []  # Return an empty list if 'results' key doesn't exist


def fetch_popular_jobs(query, location, country_code="ca"):
    base_url = "https://api.adzuna.com/v1/api/jobs"
    url = f"{base_url}/{country_code}/search/1?app_id={ADZUNA_APP_ID}&app_key={API_KEY}&location0=Canada&location1=British%20Columbia&location2=Greater Vancouver&results_per_page=50&sort_by=date&content-type=application/json&what_and={query}"
    print(url)
    response = requests.get(url)
    data = response.json()
    if "results" in data:
        jobs = data["results"]
        job_counts = {}
        for job in jobs:
            title = job["title"]
            company = (
                job["company"]["display_name"]
                if "display_name" in job["company"]
                else "Unknown"
            )
            location = job["location"]["display_name"]
            if title in job_counts:
                job_counts[title] = (job_counts[title][0] + 1, company, location)
            else:
                job_counts[title] = (1, company, location)
        sorted_job_counts = sorted(
            job_counts.items(), key=lambda x: x[1][0], reverse=True
        )
        top_jobs = [
            (job[0], job[1][0], job[1][1], job[1][2]) for job in sorted_job_counts[:5]
        ]
        return top_jobs

    else:
        return []  # Return an empty list if 'results' key doesn't exist


def create_pie_chart(df, col):
    fig = px.pie(df, names=col, title=f"Distribution of {col}")
    return fig


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=["/static/styles.css"])


def create_bar_chart(df, x_col, y_col, title):
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    return fig


def create_line_chart(df, x_col, y_col, title):
    fig = px.line(df, x=x_col, y=y_col, title=title)
    return fig


def count_keywords(text, keywords):
    count = 0
    for keyword in keywords:
        count += len(re.findall(f"(?i){keyword}", text))
    return count


# Update process_job_data to include the description field
def process_job_data(job_data):
    processed_data = []
    for job in job_data:
        company_name = (
            job["company"]["display_name"]
            if "display_name" in job["company"]
            else "Unknown"
        )
        processed_data.append(
            {
                "id": job["id"],
                "title": job["title"],
                "category": job["category"]["label"],
                "company": company_name,
                "location": job["location"]["display_name"],
                "description": job["description"],
            }
        )
    jobs_df = pd.DataFrame(processed_data)
    return jobs_df


# New function to count occurrences of skills in job descriptions
def count_skills(jobs_df, skills):
    skill_counts = {skill: 0 for skill in skills}
    for description in jobs_df["description"]:
        for skill in skills:
            if re.search(r"\b" + skill + r"\b", description, flags=re.IGNORECASE):
                skill_counts[skill] += 1
    sorted_skill_counts = sorted(
        skill_counts.items(), key=lambda x: x[1], reverse=True
    )[:20]
    return pd.DataFrame(sorted_skill_counts, columns=["skill", "count"])


# List of relevant skills to search for include all skills for all the job listings in the dataset

skills = [
    "python",
    "r",
    "java",
    "scala",
    "sql",
    "nosql",
    "hadoop",
    "spark",
    "aws",
    "azure",
    "google cloud",
    "tableau",
    "power bi",
    "excel",
    "sas",
    "matlab",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "d3",
]

# Update the callback function to generate a new bar chart based on the skills count


# Update the layout with custom styling
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Job Skills Dashboard",
                                    style={"textAlign": "center"},
                                )
                            ],
                            className="header",
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="filter-job-title",
                                    type="text",
                                    placeholder="Enter job title",
                                    value="data scientist",
                                )
                            ],
                            className="input-container",
                        ),
                    ],
                    className="title-input-container",
                ),
                html.Div(
                    [
                        html.H2(
                            "Jobs in Greater Vancouver", style={"textAlign": "center"}
                        ),
                        dash_table.DataTable(
                            id="popular-jobs-table",
                            columns=[
                                {"name": "Job Title", "id": "title"},
                                {"name": "Count", "id": "count"},
                                {"name": "Company", "id": "company"},
                                {"name": "Location", "id": "location"},
                            ],
                            style_cell={"textAlign": "left"},
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                }
                            ],
                            style_as_list_view=True,
                        ),
                    ],
                    className="table-container",
                ),
            ],
            className="grid-container",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="job-title-pie-chart")],
                    className="chart-container",
                ),
                html.Div(
                    [dcc.Graph(id="job-title-bar-chart")],
                    className="chart-container",
                ),
                html.Div(
                    [dcc.Graph(id="job-title-line-chart")],
                    className="chart-container",
                ),
                html.Div(
                    [dcc.Graph(id="job-skills-bar-chart")],
                    className="chart-container",
                ),
            ],
            className="grid2-container",
        ),
    ],
    className="container",
)


@app.callback(
    [
        Output("job-title-pie-chart", "figure"),
        Output("job-title-bar-chart", "figure"),
        Output("job-title-line-chart", "figure"),
        Output("job-skills-bar-chart", "figure"),
        Output("popular-jobs-table", "data"),
    ],
    [Input("filter-job-title", "value")],
)
def update_charts(job_title):
    job_data = fetch_job_data(job_title)
    jobs_df = process_job_data(job_data)

    pie_chart = create_pie_chart(jobs_df, "category")

    company_counts = jobs_df["company"].value_counts().reset_index()
    company_counts.columns = ["company", "count"]
    bar_chart = create_bar_chart(
        company_counts, "company", "count", "Number of Jobs per Company"
    )

    location_counts = jobs_df["location"].value_counts().reset_index()
    location_counts.columns = ["location", "count"]
    line_chart = create_line_chart(
        location_counts, "location", "count", "Number of Jobs per Location"
    )

    # Generate the job skills bar chart
    top_20_skill_counts = count_skills(jobs_df, skills)
    skill_bar_chart = create_bar_chart(
        top_20_skill_counts, "skill", "count", "Top 20 Job Skills Frequency"
    )

    # Generate the list of top 10 jobs
    top_jobs = fetch_popular_jobs(jobs_df["title"][0], jobs_df["location"][0])
    # job_list_items = [
    #     html.Li(f"{job[0]} ({job[1]})", className="list-group-item") for job in top_jobs
    # ]

    # # Generate the list of top 10 jobs with a truncate class for long texts
    # job_list_items = [
    #     html.Li(f"{job[0]} ({job[1]})", className="list-group-item truncate")
    #     for job in top_jobs
    # ]
    # top_jobs_data = [{"title": job[0], "count": job[1]} for job in top_jobs]

    table_data = [
        {"title": job[0], "count": job[1], "company": job[2], "location": job[3]}
        for job in top_jobs
    ]
    return pie_chart, bar_chart, line_chart, skill_bar_chart, table_data


if __name__ == "__main__":
    app.run_server(debug=True)
