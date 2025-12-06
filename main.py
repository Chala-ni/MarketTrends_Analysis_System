# main.py
# Main orchestrator for the AI-Powered Market Trends Analysis System.
# This script serves as the central entry point for the entire application.
# It controls the flow of execution, calling functions from other modules
# in a sequential, five-phase pipeline:
# 1. Data Collection
# 2. Data Processing
# 3. AI Enrichment
# 4. Visualization
# 5. Report Generation

import logging
import os
import pandas as pd

# Import the main functions from all our project modules.
# Each module is responsible for a specific part of the pipeline.
from api_client import get_google_trends_data, get_newsapi_articles
from scraper import scrape_news
from processor import process_and_merge_data
from llm_utils import enrich_data_with_llm
from visualizer import create_all_visualizations
from reporter import create_report

# --- Configuration & Centralized Logging ---
# Define constants for directory names to avoid hardcoding strings.
LOGS_DIR = 'logs'
DATA_DIR = 'data'
# Create these directories if they don't already exist.
# `exist_ok=True` prevents an error if the directories are already present.
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Define the full path for the log file.
log_file_path = os.path.join(LOGS_DIR, 'pipeline.log')

# This is the single point of configuration for the entire application's logging.
# By setting this up in the main script, all imported modules that use `logging.getLogger(__name__)`
# will automatically inherit this configuration.
logging.basicConfig(
    level=logging.INFO,  # Set the minimum level of messages to log (e.g., INFO, WARNING, ERROR).
    # Define the format for log messages, including timestamp, level, module name, and the message itself.
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        # The FileHandler writes log messages to the specified file.
        # 'mode='w'' means the log file is overwritten each time the pipeline runs.
        # <<< THE FIX IS HERE: Added encoding='utf-8' to handle all characters >>>
        # Using 'utf-8' encoding is crucial to prevent errors when logging special characters or emojis.
        logging.FileHandler(log_file_path, mode='w', encoding='utf-8'),
        # The StreamHandler prints log messages to the console (standard output).
        logging.StreamHandler()
    ]
)

# --- Main Pipeline Execution ---
def run_pipeline(topic):
    """
    Executes the full data pipeline from collection to final report generation.

    This function orchestrates the entire workflow by calling functions from other
    modules in the correct order. It includes checks to stop the pipeline if a critical
    step fails.

    Args:
        topic (str): The central topic for the market analysis (e.g., "Renewable Energy").
    """
    # We can remove the emojis to be 100% safe, or keep them now that the encoding is fixed.
    # Let's keep them as it proves our logging is robust.
    logging.info("=============================================")
    logging.info(f"🚀 STARTING MARKET TRENDS PIPELINE for topic: '{topic}' 🚀")
    logging.info("=============================================")

    # === PHASE 1: Data Collection ===
    # This phase gathers raw data from various sources.
    logging.info("--- Starting Phase 1: Data Collection ---")
    trends_df = get_google_trends_data(topic)
    # Critical check: If fetching Google Trends data fails, we can't proceed.
    if trends_df is None: logging.error("Google Trends failed. Stopping."); return
    # Save the raw data for archival and debugging purposes.
    trends_df.to_json(os.path.join(DATA_DIR, 'google_trends_raw.json'), orient='table', indent=4)
    
    news_df = get_newsapi_articles(topic)
    # Critical check: If fetching news articles fails, we stop the pipeline.
    if news_df is None: logging.error("NewsAPI failed. Stopping."); return
    # Save the raw news data.
    news_df.to_json(os.path.join(DATA_DIR, 'news_api_raw.json'), orient='records', indent=4)
    
    # Run the web scraper to gather additional news data.
    scrape_news()
    logging.info("--- Finished Phase 1: Data Collection ---")

    # === PHASE 2: Data Processing and Merging ===
    # This phase cleans the raw data and combines it into a single, unified dataset.
    logging.info("--- Starting Phase 2: Data Processing ---")
    if process_and_merge_data() is None:
        # If the processing function returns None, it signifies a failure.
        logging.error("Processing failed. Stopping pipeline."); return
    logging.info("--- Finished Phase 2: Data Processing ---")

    # === PHASE 3: AI Summarization and Insight Generation ===
    # This phase uses the LLM to analyze the data, adding sentiment and trend summaries.
    logging.info("--- Starting Phase 3: AI Enrichment ---")
    # The `enrich_data_with_llm` function returns a tuple (DataFrame, trends_summary).
    # We check the first element (the DataFrame) to see if the process was successful.
    if enrich_data_with_llm()[0] is None:
        logging.error("LLM enrichment failed. Stopping pipeline."); return
    logging.info("--- Finished Phase 3: AI Enrichment ---")

    # === PHASE 4: Visualization and Analysis ===
    # This phase creates plots and charts from the enriched data.
    logging.info("--- Starting Phase 4: Visualization ---")
    create_all_visualizations()
    logging.info("--- Finished Phase 4: Visualization ---")

    # === PHASE 5: Automated Report Generation ===
    # The final phase assembles all the generated insights and visualizations into a final report.
    logging.info("--- Starting Phase 5: Report Generation ---")
    create_report()
    logging.info("--- Finished Phase 5: Report Generation ---")

    # A final confirmation message indicating success.
    logging.info("===================================================")
    logging.info("✅ PIPELINE COMPLETED SUCCESSFULLY ✅")
    logging.info("===================================================")
    logging.info("All outputs have been generated in the 'data', 'reports', and 'logs' directories.")

# The `if __name__ == '__main__':` block is the standard entry point for a Python script.
# This code will only run when the script is executed directly (e.g., `python main.py`).
# It will not run if the script is imported as a module into another script.
if __name__ == '__main__':
    # Define the topic for this analysis run.
    CHOSEN_TOPIC = "Renewable Energy"
    # Call the main pipeline function to start the process.
    run_pipeline(CHOSEN_TOPIC)