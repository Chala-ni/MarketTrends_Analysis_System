# BlueOceanSP - AI-Powered Market Trends Analysis System

## Overview

This project is an AI-powered Market Trends Analysis System designed to automatically collect, process, and analyze data from multiple sources to generate insights about market trends, public interest, and media sentiment. The chosen industry for this analysis is **Renewable Energy**.

The system demonstrates a complete end-to-end data pipeline, combining data acquisition from public APIs (Google Trends, NewsAPI.org), targeted web scraping, and advanced LLM-based analysis for sentiment classification and the identification of emerging market patterns.

## Features

- **Multi-Source Data Collection:**
    - **Google Trends API:** Fetches historical public search interest data for the chosen topic.
    - **NewsAPI.org:** Gathers a broad set of recent news articles from global sources.
    - **Limited Web Scraping:** Performs a targeted scrape of a specialized industry website (`renewableenergyworld.com`) for high-quality, specific articles.
- **Data Merging & Processing:** Intelligently merges the three distinct data sources into a single, clean, and unified pandas DataFrame.
- **Efficient Batch AI Analysis:** Leverages the Google Gemini API with advanced prompt engineering for:
    - **Batch Sentiment Analysis:** Classifies the sentiment of all articles in a single, hyper-efficient API call.
    - **Emerging Trend Identification:** Analyzes all headlines to identify and summarize 3-5 major recurring market trends.
- **Comprehensive Visualization:** Generates a suite of four professional charts using `matplotlib` and `seaborn` to visualize:
    - Search Interest Trend Over Time
    - Article Sentiment Distribution
    - Top 10 Keyword Frequency
    - Data Volume by Source
- **Automated HTML Reporting:** Programmatically generates a polished, final HTML report that combines AI-generated narratives with all data visualizations and analysis summaries.

## Project Structure

```
/MarketTrends_Analysis_System/
|
├── data/
|   ├── google_trends_raw.json
|   ├── news_api_raw.json
|   ├── raw_scraped_data.json
|   └── processed_data.xlsx
|
├── logs/
|   └── pipeline.log
|
├── reports/
|   ├── visuals/
|   |   ├── trend_over_time.png
|   |   ├── sentiment_distribution.png
|   |   ├── keyword_frequency.png
|   |   └── source_comparison.png
|   |
|   └── market_trends_report.html
|
├── api_client.py
├── scraper.py
├── processor.py
├── llm_utils.py
├── visualizer.py
├── reporter.py
├── main.py
|
├── requirements.txt
├── .env
└── README.md```

## Technical Requirements

- Python 3.11
- Key Libraries:
    - `requests` & `beautifulsoup4`
    - `pandas` & `numpy`
    - `openpyxl`
    - `nltk`
    - `google-generativeai` & `python-dotenv`
    - `matplotlib`, `seaborn`, `wordcloud`
    - `pytrends` (for Google Trends API)
    - `newsapi-python` (for NewsAPI.org)

## Setup and Installation

Follow these steps to set up and run the project locally.

**1. Prerequisites:**
   - Ensure you have **Python 3.11** installed on your system.

**2. Unzip the Project:**
   - Unzip the submitted project file to a location of your choice.
   - Navigate into the project directory in your terminal:
     ```bash
     cd MarketTrends_Analysis_System
     ```

**3. Create a Virtual Environment:**
   - Create a virtual environment to isolate project dependencies.
   ```bash
   python3.11 -m venv venv
   ```

**4. Activate the Virtual Environment:**
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```

**5. Install Dependencies:**
   - Install all required packages from the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```

**6. Set Up Your API Keys:**
   - This project requires two free API keys.
   - In the main project folder, create a file named `.env`.
   - Open the `.env` file and add the following lines, pasting your keys after the `=`:
     ```
     # Get from Google AI Studio: https://aistudio.google.com/app/apikey
     GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

     # Get from NewsAPI.org: https://newsapi.org/register
     NEWS_API_KEY=YOUR_NEWSAPI_KEY_HERE
     ```

## How to Run the Pipeline

With the setup complete, you can run the entire pipeline with a single command.

**To run the full end-to-end process:**
```bash
python main.py
```
The entire pipeline is highly efficient due to batch AI processing and should complete in **approximately 1-2 minutes**.

**To run individual modules for testing:**
- `python api_client.py` (Tests the API connections)
- `python scraper.py` (Only runs the web scraper)
- `python processor.py` (Merges and cleans raw data)
- `python visualizer.py` (Generates visuals from processed data)
- `python reporter.py` (Generates the final HTML report)

## Output Description

After a successful run, the following outputs will be generated:

- **Raw Data (`/data/`):** Three JSON files containing the raw, untouched data from each source.
- **Processed Data (`/data/`):** A clean Excel file, `processed_data.xlsx`, containing the merged, cleaned, and AI-enriched dataset.
- **Visualizations (`/reports/visuals/`):** Four PNG image files for each of the generated charts.
- **Final Report (`/reports/`):** The complete, final report is available at `market_trends_report.html`. Open this file in a web browser to view it.
- **Logs (`/logs/`):** A detailed log of the pipeline's execution is saved to `pipeline.log`.
```