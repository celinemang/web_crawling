import re
import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time 


TARGET_URL = "https://www.meiji.com/global/investors/results-presentations/"
BASE_DOMAIN = "https://www.meiji.com"
API_CREATE_URL = "http://127.0.0.1:8000/create" 
MIN_YEAR = 2022

# --- Helper Functions ---

def determine_document_type(title: str) -> str:
    """
    Determines the document type based on keywords in the title.
    """
    title_lower = title.lower()
    
    #Q&A documents
    if "q&a" in title_lower:
        return "qna"   
    # Earnings Release documents
    elif "earnings release" in title_lower or "earning release" in title_lower:
        return "earnings_release"
    
    # Financial Statement documents
    elif "financial statement" in title_lower:
        return "financial_statement"
    #no document type found
    else:
        return "others"

def extract_year_and_quarter(title: str) -> tuple[Optional[int], Optional[int]]:
    """
    Extracts year and quarter from the document title.
    """
    
    # 1. Extract Year
    year = None 
    all_years = re.findall(r'(\d{4})', title)
    if all_years:
        year = int(all_years[-1])
        
    # 2. Extract Quarter
    quarter_map = {'1q': 1, '2q': 2, '3q': 3, '4q': 4}
    quarter_match = re.search(r'([1-4]Q)', title, re.IGNORECASE)
    
    quarter = None
    if quarter_match:
        quarter_str = quarter_match.group(1).lower()
        quarter = quarter_map.get(quarter_str)
        
    return year, quarter

# --- Main Crawler Logic ---

def scrape_documents() -> List[Dict[str, Any]]:
    """
    Scrapes the target URL using a headless browser (Selenium) 
    to handle lazy loading/scrolling, then extracts document details.
    """
    print(f"Starting crawl with Selenium on: {TARGET_URL}")
    
    # --- Selenium Setup ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(TARGET_URL)
    except Exception as e:
        print(f"Error starting Chrome driver: {e}")
        print("Ensure you have Chrome/Chromium installed and the corresponding WebDriver is accessible.")
        return []

    # --- Scrolling Loop for Lazy Loading ---
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scroll_attempts = 10 
    
    print("Scrolling down to load all documents...")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) 
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height or scroll_attempts >= max_scroll_attempts:
            break
            
        last_height = new_height
        scroll_attempts += 1
    
    # --- Scraping the FULL HTML Source ---
    html_source = driver.page_source
    driver.quit() 
    
    soup = BeautifulSoup(html_source, 'html5lib')

    # Broad selector to catch ALL PDF links on the page
    document_links = soup.select('a[href$=".pdf"]')
    
    if not document_links:
        print("Could not find any PDF links in the fully loaded page source.")
        return []

    crawled_data: List[Dict[str, Any]] = []
    
    for link_tag in document_links:
        title_span = link_tag.find('span')
        if title_span:
            # If a span is found, use its text
            document_title = title_span.get_text(strip=True) 
        else:
            # Fallback to the text of the <a> tag if no span is present
            document_title = link_tag.get_text(strip=True) 
        
        pdf_url = BASE_DOMAIN + link_tag['href']

        # --- Simplified Title Cleaning (PDF Only) ---
        if not document_title:
             continue
        year, quarter = extract_year_and_quarter(document_title)
        if year is None:
            # Look for a 4-digit year in the PDF URL path .../2026/...
            url_year_match = re.search(r'/(\d{4})/', pdf_url)
            if url_year_match:
                year = int(url_year_match.group(1))

        # Debug prints
        # print(f"DEBUG Title: {document_title}")
        # print(f"DEBUG year: {year}")
        # print("-" * 30)
        
        # --- MIN_YEAR FILTER (Now Active) ---
        if year is None or year < MIN_YEAR:
            print(f"--- SKIPPED: Year {year} is below MIN_YEAR ({MIN_YEAR}) or None ---")
            continue

        document_type = determine_document_type(document_title)
        
        document_data = {
            "document_title": document_title,
            "document_type": document_type,
            "year": year,
            "quarter": quarter,
            "pdf_url": pdf_url,
        }
        
        crawled_data.append(document_data)
        
    
    return crawled_data


def populate_api(documents: List[Dict[str, Any]]):
    print(f"\n Attempting to populate DB via API at: {API_CREATE_URL}")
    success_count = 0
    
    for doc in documents:
        try:
            response = requests.post(API_CREATE_URL, json=doc)
            
            if response.status_code == 201:
                success_count += 1
            elif response.status_code == 409:
                pass 
            else:
                print(f"   [FAIL] {doc['document_title']} - Status: {response.status_code}, Detail: {response.json().get('detail', 'N/A')}")
                
        except requests.exceptions.ConnectionError:
            print(f"API Connection Error. Is the FastAPI server running at {API_CREATE_URL}?")
            print("Please ensure you run 'uvicorn main:app --reload' before running the crawler.")
            return
        except Exception as e:
            print(f"An unexpected error occurred while posting data: {e}")

    print(f"\n Successfully populated/updated {success_count} documents in the database.")


if __name__ == "__main__":
    scraped_documents = scrape_documents()
    if scraped_documents:
        populate_api(scraped_documents)
