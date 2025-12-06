# reporter.py (Final Polished Version)
# This module generates the definitive HTML Market Trends Report, perfectly aligned
# with all project requirements and aesthetic feedback. It assembles AI-generated
# summaries and data visualizations into a single, self-contained HTML file.

import pandas as pd
import os
import logging
import base64  # Used to encode images for embedding directly into the HTML file.
from llm_utils import configure_llm, get_emerging_trends_summary

# --- Configuration & Helpers ---
# Set up a logger for this module.
logger = logging.getLogger(__name__)
# Define file paths for input data and output reports.
ENRICHED_FILE_PATH = os.path.join('data', 'processed_data.xlsx')
VISUALS_DIR = os.path.join('reports', 'visuals')
REPORT_OUTPUT_PATH = os.path.join('reports', 'market_trends_report.html')

def embed_image_as_base64(image_path):
    """
    Reads an image file and encodes it into a Base64 string.
    This allows the image to be embedded directly into the HTML file,
    making the report a single, portable file with no external dependencies.

    Args:
        image_path (str): The file path to the image.

    Returns:
        str: The Base64 encoded string of the image, or an empty string if the file is not found.
    """
    try:
        # Open the image file in binary read mode ('rb').
        with open(image_path, "rb") as f:
            # Read the file's binary content, encode it to Base64, and decode that to a UTF-8 string.
            return base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        # If the image doesn't exist, log a warning and return an empty string.
        logger.warning(f"Image file not found at {image_path}. It will be omitted from the report.")
        return ""

def generate_executive_summary(model, df):
    """
    Uses the configured LLM to generate a brief executive summary based on recent news headlines.

    Args:
        model: The configured generative model client.
        df (pd.DataFrame): The DataFrame containing the news data.

    Returns:
        str: The AI-generated summary, or a fallback message on failure.
    """
    logging.info("Generating executive summary...")
    # Create a string of the first 20 non-null headlines for the prompt context.
    headlines = "\\n".join("- " + str(h) for h in df['title'].dropna().head(20))
    # Construct a clear prompt for the LLM.
    prompt = f"Based on the following news headlines, write a 3-4 sentence executive summary of the current market trends for Renewable Energy.\\n\\nHeadlines:\\n{headlines}"
    try:
        # Call the model and return the generated text.
        return model.generate_content(prompt).text
    except Exception as e:
        # If the API call fails, log the error and return a user-friendly message.
        logger.error(f"Executive summary generation failed: {e}")
        return "Executive summary could not be generated due to an error."

# --- HTML Report Generation ---
def create_html_report(df, exec_summary, trends_summary_html):
    """
    Constructs the final HTML report by embedding data and visuals into a styled template.

    Args:
        df (pd.DataFrame): The main DataFrame (used for context if needed).
        exec_summary (str): The AI-generated executive summary text.
        trends_summary_html (str): The AI-generated trends summary (already in HTML format).

    Returns:
        str: The complete HTML content of the report as a single string.
    """
    logging.info("Constructing final HTML report...")
    
    # --- Embed All Four Visuals ---
    # Call the helper function to get the Base64 string for each of the four charts.
    trend_chart_b64 = embed_image_as_base64(os.path.join(VISUALS_DIR, 'trend_over_time.png'))
    sentiment_chart_b64 = embed_image_as_base64(os.path.join(VISUALS_DIR, 'sentiment_distribution.png'))
    keyword_chart_b64 = embed_image_as_base64(os.path.join(VISUALS_DIR, 'keyword_frequency.png'))
    source_chart_b64 = embed_image_as_base64(os.path.join(VISUALS_DIR, 'source_comparison.png'))

    # --- Final HTML Structure with All Polishing ---
    # This f-string acts as the template for the entire report.
    # It includes CSS for professional styling and placeholders {} for all dynamic content.
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI-Powered Market Trends Report</title>
        <style>
            /* General styling for the report's body and layout */
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; color: #333; }}
            .container {{ max-width: 950px; margin: 20px auto; padding: 25px; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 10px; }}
            .header {{ background-color: #2c3e50; color: white; padding: 25px; text-align: center; border-radius: 10px 10px 0 0; }}
            h1 {{ margin: 0; font-size: 2.8em; }}
            /* Styling for sections and headings */
            .section {{ padding: 25px; border-bottom: 1px solid #ecf0f1; }}
            .section:last-child {{ border-bottom: none; }}
            h2 {{ color: #2c3e50; font-size: 2em; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 0; }}
            h3 {{ color: #34495e; font-size: 1.5em; margin-top: 25px; }}
            h4 {{ color: #3498db; font-size: 1.3em; margin-bottom: 8px; }}
            /* Styling for text and images */
            p {{ line-height: 1.6; }}
            img {{ max-width: 100%; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>Market Trends Report: Renewable Energy</h1></div>
            <!-- Section 1: Executive Summary -->
            <div class="section">
                <h2>1. Executive Summary</h2>
                <p>{exec_summary.replace(chr(10), "<br>")}</p> <!-- Replace newline characters with HTML line breaks -->
            </div>
            <!-- Section 2: Data Sources Chart -->
            <div class="section">
                <h2>2. Overview of Data Sources</h2>
                <p>This report synthesizes data from multiple sources for a holistic market view. The chart below shows the volume of records collected from each source.</p>
                <img src="data:image/png;base64,{source_chart_b64}" alt="Data Source Comparison">
            </div>
            <!-- Section 3: Google Trends Chart -->
            <div class="section">
                <h2>3. Public Interest Over Time</h2>
                <p>Public search interest in "Renewable Energy," measured by Google Trends, shows a significant spike in late 2025, suggesting a major market or news event occurred.</p>
                <img src="data:image/png;base64,{trend_chart_b64}" alt="Trend Over Time Chart">
            </div>
            <!-- Section 4: Sentiment Analysis Chart -->
            <div class="section">
                <h2>4. Sentiment Analysis of News Coverage</h2>
                <p>The overall sentiment of news articles is largely positive, indicating confidence in the sector, though a notable number of neutral and negative articles suggest a complex and nuanced market narrative.</p>
                <img src="data:image/png;base64,{sentiment_chart_b64}" alt="Sentiment Distribution Chart">
            </div>
            <!-- Section 5: Keyword Frequency Chart -->
            <div class="section">
                <h2>5. Key Topics in News Headlines</h2>
                <p>Analysis of keywords in news headlines shows that "energy," "climate," and "power" are the most dominant topics of discussion in the current news cycle.</p>
                <img src="data:image/png;base64,{keyword_chart_b64}" alt="Keyword Frequency Chart">
            </div>
            <!-- Section 6: AI-Generated Insights -->
            <div class="section">
                <h2>6. AI Summarization and Insight Generation</h2>
                {trends_summary_html} <!-- This content is already formatted as HTML by the LLM -->
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def create_report():
    """
    The main orchestration function for this module.
    It loads data, calls the LLM for summaries, builds the HTML, and saves the final report.
    """
    logging.info("Starting final report generation...")
    try:
        # Load the fully enriched and processed data from the Excel file.
        df = pd.read_excel(ENRICHED_FILE_PATH)
    except FileNotFoundError:
        logging.error(f"Enriched data file not found at {ENRICHED_FILE_PATH}. Cannot generate report."); return

    # Configure the LLM. If it fails, use fallback text for the summaries.
    model = configure_llm()
    if not model:
        exec_summary = "LLM summary failed to generate because the model could not be configured."
        trends_summary_html = "<p>AI insights failed to generate because the model could not be configured.</p>"
    else:
        # If the model is configured, generate the dynamic summaries.
        exec_summary = generate_executive_summary(model, df)
        trends_summary_html = get_emerging_trends_summary(model, df)

    # Call the function to construct the full HTML content.
    html_content = create_html_report(df, exec_summary, trends_summary_html)
    
    try:
        # Write the generated HTML string to the output file.
        # 'encoding="utf-8"' is crucial to handle any special characters correctly.
        with open(REPORT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML report successfully saved to {REPORT_OUTPUT_PATH}")
    except IOError as e:
        logging.error(f"Failed to write HTML report to file. Error: {e}")

# This standard Python construct allows the script to be run directly for testing.
if __name__ == '__main__':
    create_report()