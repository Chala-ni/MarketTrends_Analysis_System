# visualizer.py
# This module generates all data visualizations for the Market Trends Analysis report.
# It creates four charts: Trend Over Time, Sentiment Distribution, Keyword Frequency,
# and a Data Source Comparison.

import pandas as pd
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- Configuration ---
# Set up a logger for this module.
logger = logging.getLogger(__name__)

# Define the path for the input data file (the processed and enriched Excel file).
ENRICHED_FILE_PATH = os.path.join('data', 'processed_data.xlsx')
# Define the directory where the generated chart images will be saved.
VISUALS_DIR = os.path.join('reports', 'visuals')

# --- Visualization Functions ---

def generate_trend_over_time_chart(df):
    """
    Creates and saves a line chart showing public search interest over time,
    based on Google Trends data.
    
    Args:
        df (pd.DataFrame): The main DataFrame containing all processed data.
    """
    logging.info("Generating Trend Over Time Chart...")
    try:
        # Filter the DataFrame to isolate only the data from Google Trends.
        trends_data = df[df['source'] == 'Google Trends'].copy()
        # If no Google Trends data is present, log a warning and exit the function.
        if trends_data.empty:
            logging.warning("No Google Trends data found to generate timeline chart.")
            return

        # Ensure the 'date' column is in a proper datetime format for plotting.
        trends_data['date'] = pd.to_datetime(trends_data['date'])
        
        # Set up the plot aesthetics.
        plt.figure(figsize=(12, 7))
        # Create the line plot using seaborn for a polished look.
        ax = sns.lineplot(data=trends_data, x='date', y='interest_score', marker='o', linestyle='-')
        
        # Set the titles and labels for clarity.
        ax.set_title('Search Interest Trend for "Renewable Energy" Over the Last Year', fontsize=18, fontweight='bold')
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Google Trends Interest Score (0-100)', fontsize=14)
        
        # Improve readability of the x-axis labels.
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        # Adjust layout to prevent labels from being cut off.
        plt.tight_layout()
        
        # Define the full output path and save the figure.
        output_path = os.path.join(VISUALS_DIR, 'trend_over_time.png')
        plt.savefig(output_path, dpi=300) # dpi=300 for high resolution.
        plt.close() # Close the plot to free up memory.
        logging.info(f"Chart saved to {output_path}")

    except Exception as e:
        # Catch any unexpected errors during chart generation.
        logging.error(f"Failed to generate trend over time chart. Error: {e}")

def generate_sentiment_distribution_chart(df):
    """
    Creates and saves a bar chart showing the distribution of positive, neutral,
    and negative sentiment across news articles.
    
    Args:
        df (pd.DataFrame): The main DataFrame containing all processed data.
    """
    logging.info("Generating Sentiment Distribution Chart...")
    try:
        # Filter the data to include only articles that have a valid sentiment score.
        articles_df = df[df['sentiment'].notna() & (df['sentiment'] != 'Unknown')]
        
        # Set up the plot.
        plt.figure(figsize=(10, 7))
        # Create the count plot (a type of bar chart). The order is specified for logical presentation.
        ax = sns.countplot(data=articles_df, x='sentiment', hue='sentiment', palette='viridis',
                           order=['Positive', 'Neutral', 'Negative'], legend=False)
        
        # Add count labels on top of each bar for easy reading.
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 9), textcoords='offset points',
                        fontsize=12, fontweight='bold')

        # Set titles and labels.
        ax.set_title('Distribution of Article Sentiment', fontsize=18, fontweight='bold')
        ax.set_xlabel('Sentiment', fontsize=14)
        ax.set_ylabel('Number of Articles', fontsize=14)
        
        # Define the output path and save the figure.
        output_path = os.path.join(VISUALS_DIR, 'sentiment_distribution.png')
        plt.savefig(output_path, dpi=300)
        plt.close()
        logging.info(f"Chart saved to {output_path}")
        
    except Exception as e:
        logging.error(f"Failed to generate sentiment chart. Error: {e}")

def generate_keyword_frequency_chart(df, top_n=10):
    """
    Creates and saves a horizontal bar chart displaying the most frequent keywords
    extracted from article titles and summaries.
    
    Args:
        df (pd.DataFrame): The main DataFrame.
        top_n (int): The number of top keywords to display.
    """
    logging.info("Generating Keyword Frequency Chart...")
    try:
        # Aggregate all keywords into a single list. It splits the comma-separated strings and trims whitespace.
        all_keywords = [kw.strip() for kws in df['keywords'].dropna() for kw in kws.split(',') if kw.strip()]
        # If there are no keywords, exit the function.
        if not all_keywords:
            logging.warning("No keywords to generate frequency chart.")
            return

        # Use collections.Counter to efficiently count the occurrences of each keyword and find the most common ones.
        top_keywords = Counter(all_keywords).most_common(top_n)
        # Convert the list of tuples into a DataFrame suitable for plotting.
        top_keywords_df = pd.DataFrame(top_keywords, columns=['Keyword', 'Frequency'])
        
        # Set up the plot.
        plt.figure(figsize=(12, 8))
        # Create a horizontal bar plot for better readability of keyword labels.
        ax = sns.barplot(data=top_keywords_df, x='Frequency', y='Keyword', hue='Keyword', palette='plasma', legend=False)
        
        # Set titles and labels.
        ax.set_title(f'Top {top_n} Most Frequent Keywords', fontsize=18, fontweight='bold')
        ax.set_xlabel('Frequency', fontsize=14)
        ax.set_ylabel('Keyword', fontsize=14)
        
        # Adjust layout and save the figure.
        plt.tight_layout()
        output_path = os.path.join(VISUALS_DIR, 'keyword_frequency.png')
        plt.savefig(output_path, dpi=300)
        plt.close()
        logging.info(f"Chart saved to {output_path}")
        
    except Exception as e:
        logging.error(f"Failed to generate keyword frequency chart. Error: {e}")

def generate_source_comparison_chart(df):
    """
    Creates and saves a bar chart comparing the number of records obtained
    from each data source.
    
    Args:
        df (pd.DataFrame): The main DataFrame.
    """
    logging.info("Generating Data Source Comparison Chart...")
    try:
        # Create a new, simplified 'source_category' column to group the various NewsAPI sources
        # under a single "NewsAPI.org" label for a cleaner chart.
        df['source_category'] = df['source'].apply(
            lambda x: 'Scraped' if x == 'RenewableEnergyWorld' else ('Google Trends' if x == 'Google Trends' else 'NewsAPI.org')
        )
        # Count the number of records for each category.
        source_counts = df['source_category'].value_counts().reset_index()
        source_counts.columns = ['Source', 'Count']

        # Set up the plot.
        plt.figure(figsize=(10, 7))
        # Create the bar plot.
        ax = sns.barplot(data=source_counts, x='Source', y='Count', hue='Source', palette='magma', legend=False)

        # Add count labels on top of each bar.
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 9), textcoords='offset points',
                        fontsize=12, fontweight='bold')

        # Set titles and labels.
        ax.set_title('Comparison of Data Volume by Source', fontsize=18, fontweight='bold')
        ax.set_xlabel('Data Source', fontsize=14)
        ax.set_ylabel('Number of Records', fontsize=14)
        
        # Define the output path and save the figure.
        output_path = os.path.join(VISUALS_DIR, 'source_comparison.png')
        plt.savefig(output_path, dpi=300)
        plt.close()
        logging.info(f"Chart saved to {output_path}")

    except Exception as e:
        logging.error(f"Failed to generate source comparison chart. Error: {e}")

# --- Main Orchestration Function ---
def create_all_visualizations():
    """
    The main function for this module. It loads the enriched data and then calls
    each of the specific chart-generation functions in sequence.
    """
    logging.info("Starting visualization generation...")
    
    try:
        # Load the fully processed and AI-enriched data from the Excel file.
        df = pd.read_excel(ENRICHED_FILE_PATH)
    except FileNotFoundError:
        # If the input file is missing, the process cannot continue.
        logging.error(f"Enriched data file not found at {ENRICHED_FILE_PATH}.")
        return

    # Ensure the output directory for visuals exists before trying to save files into it.
    os.makedirs(VISUALS_DIR, exist_ok=True)

    # Generate all four charts required for the report.
    generate_trend_over_time_chart(df)
    generate_sentiment_distribution_chart(df)
    generate_keyword_frequency_chart(df)
    generate_source_comparison_chart(df)
    
    logging.info("All four visualizations have been generated successfully.")

# This allows the script to be run directly for testing or standalone chart generation.
if __name__ == '__main__':
    create_all_visualizations()