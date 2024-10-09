from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pypdf
from io import BytesIO

@tool
def find_relevant_links(url: str, query: str) -> list:
    """
    Finds relevant links to webpages, Excel files, and PDF files based on the user query.

    Args:
        url (str): The URL of the website to search.
        query (str): The user query to search for relevant links.

    Returns:
        list: A list of relevant links.
    """
    relevant_links = []

    def extract_text(soup: BeautifulSoup) -> str:
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = ' '.join(element.get_text() for element in text_elements)
        return text

    def extract_text_from_pdf(pdf_url: str) -> str:
        response = requests.get(pdf_url)
        pdf_reader = pypdf.PdfReader(BytesIO(response.content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def find_relevant_subpages(text: str, link: str) -> None:
        if query.lower() in text.lower():
            relevant_links.append(link)

    def process_link(link: str) -> None:
        subpage_url = urljoin(url, link)
        if subpage_url.endswith('.pdf'):
            pdf_text = extract_text_from_pdf(subpage_url)
            find_relevant_subpages(pdf_text, subpage_url)
        else:
            subpage_response = requests.get(subpage_url)
            subpage_soup = BeautifulSoup(subpage_response.content, 'html.parser')
            subpage_text = extract_text(subpage_soup)
            find_relevant_subpages(subpage_text, subpage_url)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_text = extract_text(soup)
    find_relevant_subpages(main_text, url)

    for link in soup.find_all('a', href=True):
        process_link(link['href'])

    return relevant_links