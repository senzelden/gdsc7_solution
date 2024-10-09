from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup

@tool
def scrape_paragraph_text(url: str) -> list:
    """
    Scrapes text from all <p> elements on a webpage.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        list: A list of text content from all <p> elements.
    """
    paragraph_texts = []

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    for p in soup.find_all('p'):
        paragraph_texts.append(p.get_text())

    return paragraph_texts[:200]