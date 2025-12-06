# processor.py
# This module is the core of the data transformation pipeline.
# It correctly loads, normalizes, merges, cleans, and enriches data
# from all three sources (Google Trends, NewsAPI, Web Scraper).
# It ensures all required columns are included and formatted correctly in the final output.

import pandas as pd
import os
import logging
import re
import nltk
from collections import Counter

# --- Configuration ---
# Set up a logger for this module to record its specific operations.
logger = logging.getLogger(__name__)

# Define constants for file paths to make the script easier to read and maintain.
TRENDS_RAW_PATH = os.path.join('data', 'google_trends_raw.json')
NEWSAPI_RAW_PATH = os.path.join('data', 'news_api_raw.json')
SCRAPED_RAW_PATH = os.path.join('data', 'raw_scraped_data.json')
PROCESSED_OUTPUT_PATH = os.path.join('data', 'processed_data.xlsx')

# --- NLTK Setup & Helper Functions ---

def download_nltk_data():
    """
    Checks for required NLTK (Natural Language Toolkit) data packages
    and downloads them if they are not found. This makes the script more portable.
    """
    # A dictionary mapping the NLTK data path to its package identifier.
    required_resources = {
        "corpora/stopwords": "stopwords",  # For filtering out common words like 'the', 'a', 'is'.
        "tokenizers/punkt": "punkt",        # For splitting text into sentences and words.
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger" # For Part-of-Speech tagging (e.g., noun, verb).
    }
    try:
        # Check if each resource is already available.
        for path in required_resources.keys():
            nltk.data.find(path)
    except LookupError:
        # If a resource is not found, download all required packages.
        logging.info("Downloading NLTK data...")
        for pkg_id in required_resources.values():
            nltk.download(pkg_id, quiet=True) # 'quiet=True' suppresses verbose download output.

def clean_text(text):
    """
    A helper function to clean a string by removing non-alphabetic characters
    and converting it to lowercase.
    """
    # Return an empty string for non-string inputs to prevent errors.
    if not isinstance(text, str): return ""
    # Use regex to substitute anything that is not a letter or space with an empty string.
    return re.sub(r'[^A-Za-z\s]', '', text).lower().strip()

def extract_keywords(text, num_keywords=10):
    """
    Extracts the most common nouns from a given text to serve as keywords.
    """
    # First, clean the text to normalize it.
    cleaned_text = clean_text(text)
    # Get the standard set of English "stopwords" from NLTK.
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # Tokenize the text (split it into a list of words).
    words = nltk.word_tokenize(cleaned_text)
    # Perform Part-of-Speech (POS) tagging on the words.
    tagged_words = nltk.pos_tag(words)
    # Filter for keywords: must be a noun (tag starts with 'NN'), not a stopword, and have a length greater than 2.
    keywords = [word for word, tag in tagged_words if tag.startswith('NN') and word not in stop_words and len(word) > 2]
    # Count the occurrences of each keyword and take the most common ones.
    # Return the keywords as a single, comma-separated string.
    return ', '.join([word for word, count in Counter(keywords).most_common(num_keywords)])

# --- Main Processing Function ---
def process_and_merge_data():
    """
    Orchestrates the entire data processing workflow: loading, cleaning, merging, and enriching.
    
    Returns:
        pd.DataFrame: The final processed DataFrame on success, or None on failure.
    """
    logging.info("Starting data processing and merging phase...")
    # Ensure NLTK data is available before proceeding with text processing.
    download_nltk_data()

    # --- Step 1: Load All Data Sources ---
    try:
        # Load Google Trends data, reset the index to make the date a regular column.
        trends_df = pd.read_json(TRENDS_RAW_PATH, orient='table').reset_index().rename(columns={'index': 'date'})
        trends_df['source'] = 'Google Trends'
    except FileNotFoundError:
        logging.error(f"File not found: {TRENDS_RAW_PATH}"); return None
    try:
        # Load NewsAPI data and rename columns for consistency.
        news_df = pd.read_json(NEWSAPI_RAW_PATH).rename(columns={'publishedAt': 'date', 'description': 'summary'})
        # The 'source' column in NewsAPI data is a dictionary {'id': ..., 'name': ...}. Extract just the name.
        news_df['source'] = news_df['source'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
    except FileNotFoundError:
        logging.error(f"File not found: {NEWSAPI_RAW_PATH}"); return None
    try:
        # Load the scraped data.
        scraped_df = pd.read_json(SCRAPED_RAW_PATH)
    except FileNotFoundError:
        # If the scraped data file doesn't exist, create an empty DataFrame to prevent errors.
        logging.warning(f"Scraped data file not found at {SCRAPED_RAW_PATH}. Proceeding without it.")
        scraped_df = pd.DataFrame()

    logging.info(f"Loaded {len(trends_df)} records from Google Trends, {len(news_df)} from NewsAPI, and {len(scraped_df)} from scraping.")

    # --- Step 2: Merge and Deduplicate Article sources ---
    # Concatenate the two article sources (NewsAPI and scraped data) into a single DataFrame.
    article_df = pd.concat([news_df, scraped_df], ignore_index=True)
    # Normalize the 'date' column to datetime objects, handling potential errors and timezones.
    article_df['date'] = pd.to_datetime(article_df['date'], utc=True, errors='coerce').dt.tz_localize(None)
    # Remove any rows where the 'title' is missing, as the title is essential.
    article_df.dropna(subset=['title'], inplace=True)
    # Remove duplicate articles based on the 'title' column, keeping the first occurrence.
    article_df.drop_duplicates(subset=['title'], keep='first', inplace=True)
    logging.info(f"{len(article_df)} unique articles remain after deduplication.")

    # --- Step 3: Merge Cleaned Articles with Google Trends Data ---
    # Combine the Google Trends data with the cleaned article data.
    final_df = pd.concat([trends_df, article_df], ignore_index=True)
    # Sort the entire dataset by date in descending order (most recent first).
    final_df.sort_values(by='date', ascending=False, inplace=True)
    logging.info(f"Successfully merged all data. Total records: {len(final_df)}")

    # --- Step 4: Enrich with Keywords ---
    # Create a temporary column combining title and summary for more comprehensive keyword extraction.
    final_df['text_for_nlp'] = final_df['title'].fillna('') + ' ' + final_df['summary'].fillna('')
    # Apply the keyword extraction function to each row.
    final_df['keywords'] = final_df['text_for_nlp'].apply(extract_keywords)
    logging.info("Keyword extraction complete.")

    # --- Step 5: Finalize and Save to Excel ---
    # Define the exact column order for the final output file.
    # This ensures a consistent structure.
    # <<< THE FIX IS HERE: Added 'author' to the list of final columns >>>
    final_columns = ['date', 'source', 'title', 'author', 'summary', 'url', 'interest_score', 'keywords']
    # Reindex the DataFrame with the specified columns. Any columns not present in `final_df`
    # (like 'author' if it didn't exist in any source) will be added and filled with NaN.
    final_df = final_df.reindex(columns=final_columns)

    try:
        # Save the final, processed DataFrame to an Excel file.
        final_df.to_excel(PROCESSED_OUTPUT_PATH, index=False, engine='openpyxl')
        logging.info(f"Processed data successfully saved to {PROCESSED_OUTPUT_PATH}")
        return final_df
    except Exception as e:
        # Catch any errors during the file save operation.
        logging.error(f"Failed to save processed data to Excel. Error: {e}")
        return None

# This block allows the script to be run directly for testing purposes.
if __name__ == '__main__':
    process_and_merge_data()