from langchain_core.tools import tool
import numpy as np
import pandas as pd
import requests
from io import BytesIO
import tabula
import json
import tempfile
import re
import tabula
import pandas as pd
import requests
import json
import tempfile


@tool
def extract_table_from_url_to_string_with_auto_cleanup(pdf_url, pages='all'):
    """
    Extracts tables from a PDF URL, cleans them, and returns the data as a formatted string.
    Uses a temporary file that is automatically deleted.

    Args:
    pdf_url (str): URL to the PDF file.
    pages (str or int): Pages from which tables are extracted. 'all' for all pages or specific page numbers.

    Returns:
    str: A string representation of the cleaned extracted tables if successful, or an error message as a plain string if an error occurs.
    """
    
    def clean_table_data(tables):
        """
        Cleans the extracted tables by removing empty columns, handling missing data,
        and ensuring consistency across rows.

        Args:
        tables (list of DataFrame): List of DataFrames representing extracted tables.

        Returns:
        list of DataFrame: Cleaned tables.
        """
        cleaned_tables = []

        for table in tables:
            # Drop completely empty columns
            table = table.dropna(axis=1, how='all')

            # Drop rows with all NaN values
            table = table.dropna(how='all')

            # Optionally, fill remaining NaN with empty strings
            table = table.fillna('')

            # Filter out tables with insufficient data (e.g., less than 2 columns)
            if len(table.columns) > 1:
                cleaned_tables.append(table)

        return cleaned_tables

    try:
        # Download the PDF file
        response = requests.get(pdf_url, timeout=10)
        if response.status_code != 200:
            return f"Failed to download PDF, status code: {response.status_code}"

        # Create a temporary file that is automatically deleted upon closing
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf.flush()

            # Extract tables from the PDF using the temporary file
            tables = tabula.read_pdf(temp_pdf.name, pages=pages, multiple_tables=True, lattice=True)

            if not tables:
                return "No tables found in the PDF."

            # Clean the extracted tables
            cleaned_tables = clean_table_data(tables)
        
            # Convert the cleaned list of DataFrames to a string format
            tables_str = "\n\n".join([table.to_string(index=False) for table in cleaned_tables])

            return tables_str

    except Exception as e:
        return str(e)

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
    

@tool
def calculate_pearson_multiple(base_feature_str, feature_str_list):
    """
    Calculate the Pearson correlation coefficient between a base feature and multiple other features.
    
    Parameters:
    base_feature_str (str): A comma-separated string of numerical values representing the base feature.
    feature_str_list (list of str): A list of comma-separated strings where each string represents a numerical feature to compare with the base feature.
    
    Returns:
    dict: A dictionary where keys are 'Feature_1', 'Feature_2', etc., and values are the Pearson correlation coefficients between the base feature and each feature in the list.
    
    Raises:
    ValueError: If the lengths of the base feature and any feature in the list do not match.
    """
    try:
        # Convert base feature to a list of floats
        base_feature = [float(i) for i in base_feature_str.split(',')]

        # Dictionary to hold the correlation results
        correlation_results = {}

        for idx, feature_str in enumerate(feature_str_list):
            # Convert each feature string to a list of floats
            feature = [float(i) for i in feature_str.split(',')]

            # Ensure both lists have the same length
            if len(base_feature) != len(feature):
                raise ValueError(f"Feature at index {idx} does not have the same number of elements as the base feature.")

            # Calculate Pearson correlation for this feature
            correlation_coefficient = np.corrcoef(base_feature, feature)[0, 1]
            
            # Store result in the dictionary with the feature index as key
            correlation_results[f"Feature_{idx+1}"] = correlation_coefficient
        
        return correlation_results

    except ValueError as e:
        return f"Error: {str(e)}"
