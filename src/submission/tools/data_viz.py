from langchain_core.tools import tool
import json
import requests

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