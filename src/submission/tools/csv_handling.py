from langchain_core.tools import tool
import pandas as pd


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
def process_excel_to_json(file_name: str) -> str:
    """Read all sheets from an Excel file, combine them into a single DataFrame, 
    and return the result as a JSON string.

    Args:
        file_name (str): The name of the Excel file to process.

    Returns:
        str: A JSON string with the combined data from all sheets.
    """
    try:
        # Load the Excel file and get sheet names
        xls = pd.ExcelFile(file_name)
        sheet_names = xls.sheet_names
        
        # Read all sheets into a dictionary of DataFrames
        dfs = pd.read_excel(file_name, sheet_name=sheet_names)
        
        # Concatenate all DataFrames into one
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Convert to JSON with NaN values replaced by empty strings
        json_result = combined_df.fillna('').to_json(orient="values")
        
        return json_result
    except Exception as e:
        return f"Error processing file '{file_name}': {e}"