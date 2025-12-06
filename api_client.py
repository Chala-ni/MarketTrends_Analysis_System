# api_client.py
# This module is responsible for all data retrieval from external APIs.
# It includes functions for fetching data from Google Trends and NewsAPI.org,
# with built-in retry mechanisms for network stability.

import os
import logging
import pandas as pd
import time
from dotenv import load_dotenv
from pytrends.request import TrendReq
from newsapi import NewsApiClient

# --- Configuration ---
# Set up a logger for this module to record events and errors.
logger = logging.getLogger(__name__)
# Load environment variables from a .env file in the project root.
# This is used to securely store API keys outside of the source code.
load_dotenv()

# --- Helper Function for Retries ---
def fetch_with_retry(api_call_func, max_retries=3, delay=5):
    """
    Wraps an API call with a retry mechanism to handle transient network errors.

    Args:
        api_call_func (function): The function that performs the API call.
        max_retries (int): The maximum number of times to retry the API call.
        delay (int): The number of seconds to wait between retries.

    Returns:
        The result of the API call if successful, otherwise None.
    """
    # Loop through the specified number of retry attempts.
    for attempt in range(max_retries):
        try:
            # Attempt to execute the provided API call function and return its result.
            return api_call_func()
        except Exception as e:
            # If an exception occurs, log a warning with the attempt number and error.
            logging.warning(f"API call failed on attempt {attempt + 1}/{max_retries}. Error: {e}")
            # If this is not the last attempt, wait for the specified delay before retrying.
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                # If all retries have been exhausted, log an error and exit the loop.
                logging.error("API call failed after all retries.")
                return None

# --- Google Trends Client ---
def get_google_trends_data(keyword, timeframe='today 12-m'):
    """
    Fetches historical interest data for a keyword from Google Trends.

    Args:
        keyword (str): The search term to query.
        timeframe (str): The time period for which to fetch data (e.g., 'today 5-y', 'now 7-d').

    Returns:
        pd.DataFrame: A DataFrame containing the interest over time, or None if the call fails.
    """
    logging.info(f"Fetching Google Trends data for keyword: '{keyword}'")

    # Define the actual API call logic inside a nested function.
    # This allows it to be passed easily to the fetch_with_retry helper.
    def api_call():
        # Initialize the Pytrends request object.
        # A custom user-agent can help prevent being rate-limited or blocked.
        pytrends = TrendReq(hl='en-US', tz=360, requests_args={'headers': {'User-Agent': 'Mozilla/5.0'}})
        # Build the payload with the specified keyword and timeframe.
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='', gprop='')
        # Retrieve the interest over time data.
        trends_df = pytrends.interest_over_time()
        
        # If the DataFrame is empty, it means no data was found.
        if trends_df.empty:
            return None
        
        # Google Trends sometimes includes an 'isPartial' column which indicates
        # incomplete data. We safely drop it if it exists.
        if 'isPartial' in trends_df.columns:
            trends_df = trends_df.drop(columns=['isPartial'])
            
        # Rename the column from the keyword to a generic 'interest_score' for consistency.
        trends_df.rename(columns={keyword: 'interest_score'}, inplace=True)
        return trends_df

    # Execute the API call using the retry wrapper.
    trends_data = fetch_with_retry(api_call)
    if trends_data is not None:
        logging.info("Successfully fetched Google Trends data.")
    return trends_data

# --- NewsAPI.org Client ---
def get_newsapi_articles(keyword, page_size=30):
    """
    Fetches recent news articles for a keyword from NewsAPI.org.

    Args:
        keyword (str): The search term to find articles about.
        page_size (int): The number of articles to retrieve.

    Returns:
        pd.DataFrame: A DataFrame containing the news articles, or None if the call fails.
    """
    logging.info(f"Fetching NewsAPI.org articles for keyword: '{keyword}'")
    # Retrieve the NewsAPI key from environment variables.
    news_api_key = os.getenv("NEWS_API_KEY")
    # If the API key is not found, log an error and exit.
    if not news_api_key:
        logging.error("NEWS_API_KEY not found in .env file.")
        return None

    # Define the API call logic within a nested function to use with the retry helper.
    def api_call():
        # Initialize the NewsAPI client with the API key.
        newsapi = NewsApiClient(api_key=news_api_key)
        # Fetch articles matching the keyword, sorted by relevancy.
        all_articles = newsapi.get_everything(q=keyword, language='en', sort_by='relevancy', page_size=page_size)
        # The API response is a dictionary; extract the list of articles.
        articles = all_articles.get('articles', [])
        # Convert the list of articles (which are dictionaries) into a pandas DataFrame.
        return pd.DataFrame(articles) if articles else None

    # Execute the API call using the retry wrapper.
    articles_df = fetch_with_retry(api_call)
    if articles_df is not None:
        logging.info(f"Successfully fetched {len(articles_df)} articles from NewsAPI.org.")
    return articles_df

# --- Main Execution Block for Testing ---
# This block will only run when the script is executed directly (e.g., `python api_client.py`).
# It's used for testing the functions within this module.
if __name__ == '__main__':
    # Define a keyword for testing the API functions.
    # <<< TOPIC UPDATED HERE FOR TESTING >>>
    search_keyword = "Renewable Energy"
    
    print("\n--- Testing Google Trends API ---")
    # Call the Google Trends function.
    trends_data = get_google_trends_data(search_keyword)
    # If data was successfully retrieved, print a sample.
    if trends_data is not None:
        print("Sample of Google Trends Data:")
        print(trends_data.head())

    print("\n--- Testing NewsAPI.org API ---")
    # Call the NewsAPI function.
    news_articles_df = get_newsapi_articles(search_keyword)
    # If data was successfully retrieved, print a summary and a sample.
    if news_articles_df is not None:
        print(f"\nFound {len(news_articles_df)} news articles.")
        print(news_articles_df.head())