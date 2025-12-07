This project to reliably scrape investor documents from the Meiji website using Selenium and manage the data using a FastAPI service.

# OVERVIEW
This project has two main parts:

crawler.py: A Python script that scrapes dynamically loaded PDF links and metadata (Title, Year, Quarter).
	- Extract and store the following information for each PDF:
	    - `document_title`
	    - `document_type` (One of: `earnings_release`, `financial_statement`, `qna`, `others`)
	    - `year` (if identifiable, otherwise leave null)
	    - `quarter` (if identifiable, otherwise leave null)
	    - `pdf_url`

FastAPI Server: Handles database setup (Alembic) and provides endpoints to store and retrieve the scraped data.

# Setup and Run
1. Prerequisites
You need Python 3.8+, Google Chrome, and the corresponding Chrome WebDriver.

2. Installation
<Set up environment and install dependencies>
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Database Migration
<Initialize the local scraped_data.db file and the necessary table schema:>
    alembic upgrade head

4. Running the Project
You must run the server and the crawler in two separate terminals:

    On Terminal 1 (Server): API runs on http://127.0.0.1:8000	
        rm scraped_data.db
        alembic upgrade head
        uvicorn main:app --reload	
   

	On Terminal 2 (Crawler): crapes data and posts it to the running API.
        python crawler.py   


# Key Endpoints
Method	Endpoint	Description
POST	/create	Inserts a new document (used by the crawler).
GET	/read	Retrieves documents (supports filtering by year or document_type).
