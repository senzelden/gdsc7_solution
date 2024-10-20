from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@tool
def crawl_subpages(url: str) -> list:
    """
    Crawls a website starting from the given URL and returns a list of tuples
    containing subpage URLs and their titles, up to a depth of 1.

    Args:
        url (str): The starting URL of the website to crawl.

    Returns:
        list: A list of tuples where each tuple contains a subpage URL and its title.
    """
    def is_same_base_url(start_url, link):
        return link.startswith(start_url) and link != start_url

    def crawl(url, start_url, visited=None, subpages_list=None):
        if visited is None:
            visited = set()
        if subpages_list is None:
            subpages_list = []
        if url in visited:
            return subpages_list
        visited.add(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        subpages = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        for subpage in subpages:
            if is_same_base_url(start_url, subpage):
                subpage_response = requests.get(subpage)
                subpage_soup = BeautifulSoup(subpage_response.text, 'html.parser')
                title = subpage_soup.title.string if subpage_soup.title else 'No title'
                subpages_list.append((subpage, title))
        return subpages_list

    start_url = url
    return crawl(start_url, start_url)


@tool
def scrape_text(url: str, target_elements: list = ['p'], **attributes) -> dict:
    """
    Scrapes text from the specified target elements on a webpage.

    Args:
        url (str): The URL of the website to scrape.
        target_elements (list): A list of HTML tags to target (default is ['p']).
        **attributes: Additional attributes to filter elements (e.g., class_="highlight", id="main").

    Returns:
        dict: A dictionary where the keys are target elements and the values are lists of text content.
    """
    result = {}

    # Send HTTP request
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Iterate over each target element type
    for target_element in target_elements:
        texts = []

        # Find all elements that match the target tag and attributes
        for element in soup.find_all(target_element, **attributes):
            text = element.get_text()
            if '.' in text:  # Optional filtering for text with periods
                texts.append(text)
        
        # Store the result for each target element
        result[target_element] = texts[:7]  # Return only the first 8 texts for brevity

    return result


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
        text = p.get_text()
        if '.' in text:
            paragraph_texts.append(text)

    return paragraph_texts[:5]


@tool
def get_unesco_data(indicators: list, geo_units: list, start: str = '2021', end: str = '2021', indicator_metadata: bool = False) -> dict:
    """
    Sends a GET request to the UNESCO API (https://api.uis.unesco.org/api/public) to retrieve data for multiple indicators.

    Args:
        indicators (list): A list of indicator codes to query.
        geo_units (list): A list of geographic units (countries) to include in the query.
        start (str): The start year for the data query. Defaults to '2021'.
        end (str): The end year for the data query. Defaults to '2021'.
        indicator_metadata (bool, optional): Whether to include indicator metadata in the response. Defaults to False.

    Returns:
        dict: The JSON response from the UNESCO API if the request is successful.
              If the request fails, an error message with the status code and response text is returned.

    Example usage:
        get_unesco_data(indicators=['XGDP.FSGOV', 'XGDP.EDU'], geo_units=['BRA', 'USA', 'DEU'])
    """
    base_url = 'https://api.uis.unesco.org/api/public/data/indicators'
    params = {
        'start': start,
        'end': end,
        'indicatorMetadata': str(indicator_metadata).lower()
    }

    # Add indicator parameters
    for indicator in indicators:
        params.setdefault('indicator', []).append(indicator)

    # Add geoUnit parameters
    for geo_unit in geo_units:
        params.setdefault('geoUnit', []).append(geo_unit)

    try:
        # Send GET request with the specified parameters
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError if the response status code is 4xx or 5xx

        # Parse the response JSON
        return response.json()

    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the request
        return {"error": f"Request to UNESCO API failed: {e}"}