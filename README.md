# Job Skills Dashboard

This is a simple dashboard that allows users to search for job postings related to a specific job title and see various visualizations related to those job postings.

## Requirements

### macOS
- Python 3.6 or later
- pip3
- A web browser

### Windows
- Python 3.6 or later
- A web browser

## Installation

1. Clone the repository: `git clone https://github.com/Ollstar/job-skills-dashboard.git`
2. Navigate to the project directory: `cd job-skills-dashboard`
3. Install the required packages: `pip3 install -r requirements.txt`
4. Rename the `.env.example` file to `.env` and add your Adzuna API key and app ID. If you don't have an API key, you can sign up for one at https://developer.adzuna.com/overview.
5. Run the app:
   - macOS: `python3 app.py`
   - Windows: `python app.py`
6. Navigate to `http://127.0.0.1:8050/` in your web browser to view the dashboard.

## Usage

To use the dashboard, simply enter a job title in the input field and click the "Search" button. The dashboard will then display various visualizations related to job postings related to that job title, including:

- A pie chart showing the distribution of job categories
- A bar chart showing the number of job postings per company
- A line chart showing the number of job postings per location
- A bar chart showing the frequency of the top 20 job skills mentioned in job descriptions
- A table showing the top 10 most popular jobs in the Greater Vancouver area

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
