# ScrapeX: AI-Powered Scraper

ScrapeX is a Streamlit-based web application that leverages Google Generative AI to search for company information and analyze leads in real-time. This tool combines data scraping and heuristic techniques to gather details such as company name, website, email, LinkedIn profile, and headquarters location, and then evaluates the lead quality based on this data.

## Features
* **Company Information Search**: Uses Google Generative AI to retrieve official company details in JSON format.
* **Lead Analysis**: Performs real-time lead analysis using heuristic methods to determine a "Lead Score" (High, Medium, or Low) along with a corresponding "Scoring Reason".
* **Data Saving**: Saves the scraped data in CSV (and optionally Excel) format for further reference and analysis.
* **Data and Score Updates**: Provides options to update both the saved data and lead scoring in real-time.

## Requirements
* Python 3.8 or higher
* Libraries:
 * Streamlit
 * Pandas
 * google-generativeai

## Installation
1. Clone the repository:
   ```bash git clone https://github.com/yourusername/scrapex.git```
   ```cd scrapex ```
2. Install dependencies on file "dependencies.ipynb"

## How to Run the Application
1. Run Streamlit ```streamlit run scrapex_interface.py``` or ```python -m streamlit run scrapex_interface.py```
2. Use the application: Open the URL provided in your browser. Enter a company name in the input field and click Analyze to perform the scraping and lead analysis.

## Code Structure
1. **scrapex_class.py**: Contains the ```Scrapex``` class that handles company information search, lead analysis, and data saving functionality.
2. **scrapex_interface.py**: The Streamlit-based user interface that connects the Scrapex class functions with the web view. This file enables you to perform scraping, analysis, data updates, and CSV downloads.
