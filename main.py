from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the Country Outline API!"}


# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline", response_class=PlainTextResponse)
def get_country_outline(country: str = Query(..., min_length=1)):
    # Construct the Wikipedia URL
    wikipedia_url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    # Fetch the Wikipedia page
    response = requests.get(wikipedia_url)
    if response.status_code != 200:
        return f"# Error\n\nCould not retrieve Wikipedia page for '{country}'."

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract headings (h1-h6)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # Markdown output
    markdown_lines = ["## Contents", f"# {country.strip()}"]
    
    # List of section titles to skip
    SKIP_HEADINGS = {"references", "external links", "see also", "further reading", "notes", "contents"}

    for tag in headings:
        text = tag.get_text().strip()
        if text.lower() in SKIP_HEADINGS:
            continue  # Skip unwanted sections
        level = int(tag.name[1])  # h1 -> 1, h2 -> 2, ...
        markdown_lines.append(f"{'#' * (level+1)} {text}")


    return "\n\n".join(markdown_lines)
