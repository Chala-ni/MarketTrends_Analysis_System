# llm_utils.py
# This module uses a highly efficient "batch processing" approach to minimize API calls
# and complete the AI analysis in seconds instead of minutes.

import pandas as pd
import os
import logging
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configuration ---
# Set up a logger for this module to record events and errors.
logger = logging.getLogger(__name__)
# Load environment variables from a .env file (e.g., for API keys).
load_dotenv()
# Define a constant for the path to the processed data file to avoid hardcoding.
PROCESSED_FILE_PATH = os.path.join('data', 'processed_data.xlsx')

# --- LLM Setup ---
def configure_llm():
    """
    Configures and returns the Google Gemini model client.
    This function handles API key retrieval and model initialization.
    """
    # Retrieve the Gemini API key from environment variables.
    api_key = os.getenv("GEMINI_API_KEY")
    # If the API key is not found, log an error and return None.
    if not api_key:
        logging.error("GEMINI_API_KEY not found in .env file.")
        return None
    try:
        # Configure the generative AI library with the API key.
        genai.configure(api_key=api_key)
        # Initialize the specific Gemini model to be used.
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        logging.info("Google Gemini model configured successfully.")
        return model
    except Exception as e:
        # Catch any exceptions during configuration and log an error.
        logging.error(f"Failed to configure Google Gemini. Error: {e}")
        return None

# --- AI Task 1: BATCH Sentiment Classification ---
def get_sentiment_in_batch(model, df):
    """
    Analyzes sentiment for ALL articles in a single, efficient API call.
    This batching approach is significantly faster than analyzing one by one.

    Args:
        model: The configured generative model client.
        df (pd.DataFrame): The DataFrame containing article data.

    Returns:
        dict: A dictionary mapping article index to its sentiment string, or an empty dict on failure.
    """
    logging.info("Starting BATCH sentiment analysis...")
    
    # We only need to analyze articles that have a title, so we filter them out.
    articles_df = df[df['title'].notna()].copy()
    
    # Create a simple numbered list of headlines to be included in the prompt.
    # This format is easy for the LLM to parse.
    headline_list = ""
    for index, row in articles_df.iterrows():
        # Using the original DataFrame index as a unique ID for each headline.
        # This allows us to map the results back correctly.
        headline_list += f"{index}: \"{row['title']}\"\\n"

    # This powerful prompt instructs the AI to return a single JSON object.
    # This is the key to the batch processing technique. It avoids multiple API calls
    # and makes the response easy to parse automatically.
    prompt = f"""
    Analyze the sentiment for each numbered headline in the following list.
    Your response MUST be a single, valid JSON object.
    The keys of the JSON object must be the integer ID of each headline.
    The values must be one of three exact strings: "Positive", "Negative", or "Neutral".

    Example Output:
    {{
      "0": "Positive",
      "5": "Negative",
      "12": "Neutral"
    }}

    Headlines to Analyze:
    {headline_list}
    """
    
    try:
        # Send the single, comprehensive prompt to the model.
        response = model.generate_content(prompt)
        # Clean the response text to ensure it's valid JSON.
        # LLMs sometimes wrap JSON in markdown backticks (```json ... ```), which we remove.
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        # Parse the cleaned JSON string into a Python dictionary.
        sentiments_dict = json.loads(cleaned_response)
        
        logging.info("Successfully received batch sentiment analysis from LLM.")
        return sentiments_dict
        
    except Exception as e:
        # If any part of the process fails (API call, JSON parsing), log the error.
        logging.error(f"Batch sentiment analysis failed. Error: {e}")
        return {} # Return an empty dict on failure to prevent crashes downstream.

# --- AI Task 2: Trend Identification (Unchanged) ---
def get_emerging_trends_summary(model, df):
    """
    Analyzes all article headlines to identify 3-5 major recurring trends.
    
    Args:
        model: The configured generative model client.
        df (pd.DataFrame): The DataFrame containing article titles.
        
    Returns:
        str: An HTML-formatted string summarizing the trends, or an error message.
    """
    # This function is already efficient as it processes all headlines in one call.
    logging.info("Generating high-level summary of emerging trends...")
    # Extract non-null titles into a list.
    headlines = df[df['title'].notna()]['title'].tolist()
    # Format the list of headlines for the prompt.
    headlines_str = "\\n".join(f"- {h}" for h in headlines)
    # The prompt asks the model to act as a market analyst and provide a formatted summary.
    prompt = f"""
    As a market analyst, analyze the following headlines about Renewable Energy and identify 3-5 major recurring topics.
    Format your response as simple HTML, using <h4> for each topic title and <p> for its description.
    Do not include any other HTML tags.
    Headlines:
    {headlines_str}
    """
    try:
        # Generate the content based on the prompt.
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Failed to generate trends summary. Error: {e}")
        # Return a user-friendly error message in HTML format.
        return "<p>Error generating trends summary.</p>"

# --- Main Orchestration Function ---
def enrich_data_with_llm():
    """
    Orchestrates the entire AI enrichment phase using the efficient batch method.
    It reads the data, calls the AI functions, and saves the updated data.
    
    Returns:
        tuple: A tuple containing the enriched DataFrame and the trends summary HTML string.
    """
    logging.info("Starting AI enrichment phase...")
    
    try:
        # Load the pre-processed data from the specified Excel file.
        df = pd.read_excel(PROCESSED_FILE_PATH)
    except FileNotFoundError:
        logging.error(f"Processed data file not found at {PROCESSED_FILE_PATH}.")
        return None, None

    # Configure the Gemini model. If it fails, stop execution.
    model = configure_llm()
    if not model: return None, None
        
    # --- Perform Batch Sentiment Analysis (1 API Call) ---
    # This single call gets sentiments for all articles.
    sentiments_dict = get_sentiment_in_batch(model, df)
    
    if sentiments_dict:
        # Map the dictionary results back to the DataFrame to add the 'sentiment' column.
        # The keys in the dict are strings from the JSON, so we convert the DataFrame index
        # to strings to ensure a correct match.
        # .fillna('Unknown') handles any articles that might not have been in the dict.
        df['sentiment'] = df.index.to_series().astype(str).map(sentiments_dict).fillna('Unknown')
    else:
        # If the sentiment analysis failed, fill the column with a default value.
        df['sentiment'] = 'Unknown'

    # --- Generate Overall Trends Summary (1 API Call) ---
    # We add a short delay here as a polite practice to avoid overwhelming an API endpoint,
    # even though we are using a different one.
    time.sleep(1) 
    trends_summary_html = get_emerging_trends_summary(model, df)
    
    # --- Save the Updated DataFrame ---
    try:
        # Save the enriched DataFrame back to the same Excel file, overwriting it.
        df.to_excel(PROCESSED_FILE_PATH, index=False, engine='openpyxl')
        logging.info(f"Successfully saved enriched data back to {PROCESSED_FILE_PATH}")
    except Exception as e:
        logging.error(f"Failed to save enriched data to Excel. Error: {e}")

    # Return the final results for use in other parts of the application.
    return df, trends_summary_html

# This block runs only when the script is executed directly.
# It serves as a convenient way to run the entire data enrichment process for testing.
if __name__ == '__main__':
    enrich_data_with_llm()