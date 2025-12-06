# scraper.py
# This module is responsible for the "limited web scraping" task.
# It scrapes 5-10 articles from a specified news source, visiting each article's
# page to gather detailed information including title, date, author, and summary.

import requests
from bs4 import BeautifulSoup
import json
import os
import logging
import time

# --- Configuration ---
# Set up a logger for this module to record its specific operations.
logger = logging.getLogger(__name__)

# Define the base URL of the website to be scraped.
BASE_URL = "https://www.renewableenergyworld.com"
# Set a limit for the number of articles to scrape, as per the project requirement (5-10).
ARTICLE_LIMIT = 10
# Define the path for the output file where the raw scraped data will be stored.
OUTPUT_FILE_PATH = os.path.join('data', 'raw_scraped_data.json')

# --- Main Scraping Function ---
def scrape_news():
    """
    Orchestrates the scraping process. It performs a two-step scrape:
    1. Fetches a list of article links from the main homepage.
    2. Visits each individual article page to extract detailed information like author and date.
    
    Returns:
        list: A list of dictionaries, where each dictionary represents a scraped article.
              Returns None on a critical failure (e.g., cannot reach the homepage).
    """
    logging.info("Starting limited web scraping process...")
    # Using a requests.Session() object is good practice as it persists certain parameters (like headers)
    # across requests made from the same session.
    session = requests.Session()
    # Setting a User-Agent header helps mimic a real web browser, which can prevent
    # the request from being blocked by some websites.
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    # --- Step 1: Fetch and parse the homepage to find article links ---
    try:
        # Make the HTTP GET request to the base URL.
        homepage_response = session.get(BASE_URL)
        # This will raise an HTTPError if the HTTP request returned an unsuccessful status code (e.g., 404, 500).
        homepage_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # If the homepage can't be fetched, the scraper cannot proceed. Log a critical error and exit.
        logging.error(f"Failed to fetch homepage {BASE_URL}. Error: {e}")
        return None

    # Parse the HTML content of the homepage using BeautifulSoup.
    soup = BeautifulSoup(homepage_response.content, 'html.parser')
    # Find all 'div' elements with the class 'post-item', which are the containers for each article summary.
    # We fetch a few more than the limit to account for any items that might not be valid articles.
    article_blocks = soup.find_all('div', class_='post-item', limit=ARTICLE_LIMIT + 5)
    
    # If no article blocks are found, it might indicate a change in the website's structure.
    if not article_blocks:
        logging.warning("No article blocks found on the homepage. The website layout may have changed.")
        return None

    logging.info(f"Found {len(article_blocks)} potential articles. Scraping details for up to {ARTICLE_LIMIT}...")
    scraped_articles = []
    
    # --- Loop through each article block found on the homepage ---
    for article_block in article_blocks:
        # Stop scraping once we have reached the desired number of articles.
        if len(scraped_articles) >= ARTICLE_LIMIT:
            break

        # Find the title element within the article block.
        title_element = article_block.find('h3', class_='m-none')
        # Ensure the title element and its anchor tag exist before proceeding.
        if not title_element or not title_element.a:
            continue # Skip this block if it's not a valid article link.
            
        # Extract the URL from the 'href' attribute of the anchor tag.
        article_url = title_element.a['href']
        # Handle relative URLs (e.g., '/p/solar-power') by prepending the base URL.
        if not article_url.startswith('http'):
            article_url = f"{BASE_URL}{article_url}"
            
        # --- Step 2: Visit the individual article page for detailed information ---
        try:
            logging.info(f"Visiting article: {article_url}")
            # Make a GET request to the specific article's URL.
            article_response = session.get(article_url, timeout=10)
            article_response.raise_for_status()
            # Parse the HTML content of the article page.
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # Extract the author's name from a span with a specific class.
            author_span = article_soup.find('span', class_='meta-author-name')
            author = author_span.get_text(strip=True) if author_span else "Not specified"

            # Extract the publication date, which is reliably found in a meta tag.
            date_meta = article_soup.find('meta', property='article:published_time')
            date = date_meta['content'] if date_meta else None

            # Assemble all the extracted data into a dictionary.
            scraped_articles.append({
                'title': title_element.get_text(strip=True),
                'date': date,
                'author': author,
                # The summary is available on the homepage block.
                'summary': article_block.find('div', class_='description').get_text(strip=True) if article_block.find('div', class_='description') else "",
                'url': article_url,
                'source': 'RenewableEnergyWorld'
            })
            # Add a small, polite delay between requests to avoid overwhelming the server.
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            # If a single article page fails to load, log a warning and continue to the next one.
            # This makes the scraper resilient to individual page errors.
            logging.warning(f"Could not fetch or process article at {article_url}. Skipping. Error: {e}")

    logging.info(f"Successfully scraped {len(scraped_articles)} articles with full details.")
    
    # --- Step 3: Save the collected data to a JSON file ---
    try:
        # Ensure the 'data' directory exists before trying to write the file.
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
        # Open the output file in write mode with UTF-8 encoding.
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            # Dump the list of article dictionaries into the file as a JSON object.
            # `indent=4` makes the JSON file human-readable.
            # `ensure_ascii=False` allows for proper saving of non-ASCII characters.
            json.dump(scraped_articles, f, indent=4, ensure_ascii=False)
        logging.info(f"Raw scraped data successfully saved to {OUTPUT_FILE_PATH}")
        return scraped_articles
        
    except IOError as e:
        # If the file cannot be written, log an error.
        logging.error(f"Failed to write data to {OUTPUT_FILE_PATH}. Error: {e}")
        return None

# This standard Python construct allows the script to be run directly from the command line
# for testing or standalone execution.
if __name__ == '__main__':
    scrape_news()