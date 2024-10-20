from langchain_core.tools import tool
import json
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import boto3
from uuid import uuid4
from io import BytesIO


@tool
def create_quickchart_url(
    chart_input: dict
) -> str:
    """
    Sends a POST request to the QuickChart API (https://quickchart.io/chart) to generate a chart, and returns the URL for the created chart.

    Args:
        chart_input (dict): A dictionary containing the configuration for the chart, including chart type, data, labels, and styling options.

    Returns:
        str: The URL of the generated chart if the request is successful.
             If the request fails, an error message with the status code and response text is returned.

    Example of dictionary:
        {
            "format": "svg",  # Specifies the image format (e.g., 'png' or 'svg')
            "chart": {
                "type": "bar",  # Type of the chart, such as 'bar', 'line', or 'pie'
                "data": {
                    "labels": ["Income Level", "Parental Education", "School Funding"],  # X-axis labels for chart categories
                    "datasets": [
                        {
                            "label": "Low Performance",  # Dataset label for low performance group
                            "data": [60, 65, 58],  # Corresponding values for the low performance group
                            "backgroundColor": "#DA9A8B"  # Color for the dataset bar (red)
                        },
                        {
                            "label": "Medium Performance",  # Dataset label for medium performance group
                            "data": [75, 78, 76],  # Corresponding values for the medium performance group
                            "backgroundColor": "#DCBB7C"  # Color for the dataset bar (orange)
                        },
                        {
                            "label": "High Performance",  # Dataset label for high performance group
                            "data": [90, 88, 85],  # Corresponding values for the high performance group
                            "backgroundColor": "#4FB293"  # Color for the dataset bar (green)
                        }
                    ]
                },
                "options": {
                    "title": {
                        "display": True,
                        "text": "Reading Scores vs Socioeconomic Factors"  # Chart title
                    },
                    "scales": {
                        "xAxes": [{
                            "scaleLabel": {
                                "display": True,
                                "labelString": "Socioeconomic Factors"  # Label for the x-axis
                            }
                        }],
                        "yAxes": [{
                            "scaleLabel": {
                                "display": True,
                                "labelString": "Reading Scores"  # Label for the y-axis
                            }
                        }]
                    },
                    "legend": {
                        "display": True,  # Determines if the legend should be displayed
                        "position": "bottom"  # Position of the legend
                    }
                }
            }
        }

    Example usage:
        create_quickchart_url(chart_input)

    """
    api_url = 'https://quickchart.io/chart/create'

    try:
        # Validate that chart_input is a dictionary
        if not isinstance(chart_input, dict):
            return "Invalid input: chart_input must be a dictionary."

        # Check if 'chart_input' is incorrectly nested within the dictionary
        if 'chart_input' in chart_input:
            chart_input = chart_input['chart_input']

        # Ensure the value of chart_input is a dictionary and not a string
        if isinstance(chart_input, str):
            try:
                chart_input = json.loads(chart_input)
            except json.JSONDecodeError:
                return "Invalid input: chart_input string could not be parsed as a dictionary."
        
        # Check if the dictionary is empty
        if not chart_input:
            return "Invalid input: chart_input cannot be an empty dictionary."
        
        # Send POST request with the chart input
        response = requests.post(api_url, json=chart_input, timeout=10)
        response.raise_for_status()  # Raise HTTPError if the response status code is 4xx or 5xx
        
        # Parse the response JSON and extract the chart URL
        result = response.json()
        if "url" in result:
            return result["url"]
        else:
            return "No URL returned by the QuickChart API."

    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the request
        return f"Request to QuickChart API failed: {e}"
    


@tool
def custom_plot_from_string_to_s3(plot_code_string):
    """
    Executes custom plot code from a string, generates a seaborn plot,
    uploads it to S3, and returns the S3 URL.

    Args:
        plot_code_string (str): String containing the custom plotting code.

    Returns:
        str: Public URL of the uploaded image in S3.
    
    Example:
        plot_code_string = 
            '''
            import seaborn as sns
            import pandas as pd

            # Set the theme for the plot
            sns.set_theme(style="white")

            # Define the dataset directly
            mpg_data = {
                "mpg": [18, 15, 16, 17, 14, 12, 13, 19, 20, 21],
                "horsepower": [130, 165, 150, 140, 198, 220, 215, 110, 105, 95],
                "weight": [3504, 3693, 3436, 3433, 4341, 4354, 4312, 4498, 4464, 4425],
                "origin": ["USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "USA", "Europe"]
            }

            # Convert the dataset to a pandas DataFrame
            mpg = pd.DataFrame(mpg_data)

            # Plot miles per gallon against horsepower with other semantics
            fig = sns.relplot(x="horsepower", y="mpg", hue="origin", size="weight",
                              sizes=(40, 400), alpha=.5, palette="muted",
                              height=6, data=mpg)
            '''
    """
    
    try:
        # Prepare a dictionary to capture variables from exec
        local_vars = {}
        
        # Execute the custom plotting code and capture local variables
        exec(plot_code_string, {}, local_vars)
        
        # Get the 'fig' variable from the executed code
        fig = local_vars.get('fig', None)
        
        if fig is None:
            raise ValueError("The code did not produce a 'fig' object.")
        
        # Save the plot to a temporary file (in memory)
        img_data = BytesIO()
        fig.savefig(img_data, format='png')
        plt.close()
        img_data.seek(0)
        
        # Initialize a boto3 session and S3 client
        session = boto3.Session()
        s3 = session.client('s3')
        bucket_name = "gdsc-bucket-381492151587"
        object_name = f"seaborn_charts/{uuid4()}.png"
        
        # Upload the image to S3 using upload_fileobj
        try:
            s3.upload_fileobj(img_data, bucket_name, object_name)
            # Build and return the S3 URL
            s3_url = f'https://{bucket_name}.s3.amazonaws.com/{object_name}'
            print(f"Image successfully uploaded to: {s3_url}")
            return s3_url
        except Exception as e:
            print(f"An error occurred during the upload: {e}")
            return f"An error occurred: {str(e)}"
    
    except Exception as e:
        print(f"Error occurred while creating plot: {e}")
        raise