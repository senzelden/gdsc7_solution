from langchain_core.tools import tool
import numpy as np
import statsmodels.api as sm


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

            # Check for constant feature (standard deviation is zero)
            if np.std(feature) == 0 or np.std(base_feature) == 0:
                correlation_coefficient = np.nan
            else:
                # Calculate Pearson correlation for this feature
                correlation_coefficient = np.corrcoef(base_feature, feature)[0, 1]
            
            # Store result in the dictionary with the feature index as key
            correlation_results[f"Feature_{idx+1}"] = correlation_coefficient
        
        return correlation_results

    except ValueError as e:
        return f"Error: {str(e)}"

@tool
def calculate_quantile_regression_multiple(base_feature_str, feature_str_list, quantiles=[0.25, 0.5, 0.75]):
    """
    Perform quantile regression between a base feature and multiple other features for multiple quantiles.
    
    Parameters:
    base_feature_str (str): A comma-separated string of numerical values representing the base feature.
    feature_str_list (list of str): A list of comma-separated strings where each string represents a numerical feature to compare with the base feature.
    quantiles (list of float): A list of quantiles to be used for regression (default is [0.25, 0.5, 0.75]).
    
    Returns:
    dict: A dictionary where keys are 'Feature_1', 'Feature_2', etc., and values are dictionaries with quantiles as keys and regression coefficients as values.
    
    Raises:
    ValueError: If the lengths of the base feature and any feature in the list do not match.
    TypeError: If the input types are not as expected.
    ValueError: If the quantiles are not within the range [0, 1].
    """
    try:
        # Check input types
        if not isinstance(base_feature_str, str) or not all(isinstance(f, str) for f in feature_str_list):
            raise TypeError("Base feature and feature list must be strings and list of strings, respectively.")
        
        # Check for empty inputs
        if not base_feature_str or not feature_str_list:
            raise ValueError("Base feature string and feature list cannot be empty.")
        
        # Convert base feature to a list of floats
        base_feature = [float(i) for i in base_feature_str.split(',')]
        base_feature = np.array(base_feature)

        # Dictionary to hold the regression results
        regression_results = {}

        for idx, feature_str in enumerate(feature_str_list):
            # Convert each feature string to a list of floats
            feature = [float(i) for i in feature_str.split(',')]
            feature = np.array(feature)

            # Ensure both lists have the same length
            if len(base_feature) != len(feature):
                raise ValueError(f"Feature at index {idx} does not have the same number of elements as the base feature.")

            # Add a constant term for the intercept
            feature = sm.add_constant(feature)

            # Dictionary to hold the results for each quantile
            quantile_results = {}

            for quantile in quantiles:
                # Check if quantile is within the valid range
                if not (0 <= quantile <= 1):
                    raise ValueError(f"Quantile {quantile} is out of range. Must be between 0 and 1.")

                # Perform quantile regression
                model = sm.QuantReg(base_feature, feature)
                result = model.fit(q=quantile)
                
                # Store result in the dictionary with the quantile as key
                quantile_results[quantile] = result.params.tolist()
            
            # Store the quantile results in the main dictionary with the feature index as key
            regression_results[f"Feature_{idx+1}"] = quantile_results
        
        return regression_results

    except (ValueError, TypeError) as e:
        return f"Error: {str(e)}"
