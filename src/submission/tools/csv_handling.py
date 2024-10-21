from langchain_core.tools import tool
import pandas as pd
import requests
from io import BytesIO


@tool
def csv_to_json_string(file_path: str, sep: str = ";") -> str:
    """
    Reads a CSV file, converts it to JSON, and returns the JSON string.

    Args:
        file_path (str): The path to the CSV file.
        sep (str): The delimiter to use. Default is ';'.

    Returns:
        str: A JSON string representation of the DataFrame.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path, sep=sep)
        
        # Convert DataFrame to JSON
        json_data = df.to_json(orient='records')
        
        # Convert JSON to string
        json_string = str(json_data)
        
        return json_string
    except Exception as e:
        return f"An error occurred: {e}"
    

    import pandas as pd

    
@tool
def process_first_sheet_to_json_from_url(url: str) -> str:
    """Download an Excel file from the internet, read the first sheet, and return the result as a JSON string.

    Args:
        url (str): The URL of the Excel file to process.

    Returns:
        str: A JSON string with the data from the first sheet.
    """
    try:
        # Download the Excel file from the URL
        response = requests.get(url)
        response.raise_for_status()  # Check for download errors
        
        # Load the Excel file from the downloaded content
        xls = pd.ExcelFile(BytesIO(response.content))
        
        # Read only the first sheet into a DataFrame
        first_sheet_df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
        
        # Convert to JSON with NaN values replaced by empty strings
        json_result = first_sheet_df.fillna('').to_json(orient="values")
        
        return json_result
    except Exception as e:
        return f"Error processing file from URL '{url}': {e}"