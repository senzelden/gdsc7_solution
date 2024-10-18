from langchain_core.tools import tool
import requests

@tool
def create_quickchart_url(chart_input):
    """
    Sends a POST request to the QuickChart API to create a chart and returns the URL of the generated chart.

    Args:
        chart_input (dict): A dictionary containing the chart configuration to be sent to the QuickChart API.

    Returns:
        str: The URL of the generated chart if the request is successful.
             If the request fails, returns an error message with the status code and response text.

    Example:
        chart_input = {
            "chart": {
                "type": "bar",  # Bar chart type
                "data": {
                    "labels": ["Income Level", "Parental Education", "School Funding"],  # X-axis labels
                    "datasets": [
                        {
                            "label": "Low Performance",  # Label for low performance
                            "data": [60, 65, 58],  # Reading scores for low performance
                            "backgroundColor": "#DA9A8B"  # Red color
                        },
                        {
                            "label": "Medium Performance",  # Label for medium performance
                            "data": [75, 78, 76],  # Reading scores for medium performance
                            "backgroundColor": "#DCBB7C"  # Orange color
                        },
                        {
                            "label": "High Performance",  # Label for high performance
                            "data": [90, 88, 85],  # Reading scores for high performance
                            "backgroundColor": "#4FB293"  # Green color
                        }
                    ]
                },
                "options": {
                    "title": {
                        "display": True,
                        "text": "Reading Scores vs Socioeconomic Factors"
                    },
                    "scales": {
                        "xAxes": [{
                            "scaleLabel": {
                                "display": True,
                                "labelString": "Socioeconomic Factors"
                            }
                        }],
                        "yAxes": [{
                            "scaleLabel": {
                                "display": True,
                                "labelString": "Reading Scores"
                            }
                        }]
                    },
                    "legend": {
                        "display": True,
                        "position": "bottom"
                    }
                }
            }
        } 
        url = create_quickchart_url(chart_input)
        print(url)  # Outputs the URL of the generated chart or an error message.
    """
    api_url = 'https://quickchart.io/chart/create'
    
    try:
        response = requests.post(api_url, json=chart_input, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        if "url" in result:
            return result["url"]
        else:
            return "No URL returned"
    
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"