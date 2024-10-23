from langchain_core.tools import tool
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, pearsonr, f_oneway, chi2_contingency
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import statsmodels.api as sm
from statsmodels.multivariate.manova import MANOVA
from io import StringIO

@tool
def analyze_pirls_data(input_string, df_string):
    """
    Function to analyze PIRLS-related problems using statistical methods based on the input string.
    
    This function dynamically extracts column names from the input_string and performs the specified
    statistical test using a provided DataFrame in CSV string format. The input_string should contain 
    both the type of analysis and the columns involved.
    
    Supported statistical analyses include:
    - T-test: "t-test on ColA and ColB"
    - Correlation: "correlation between ColX and ColY"
    - ANOVA: "anova on ColA by ColB"
    - Linear Regression: "linear regression using Col1, Col2, ..., ColN"
    - Chi-Square Test: "chi-square between ColA and ColB"
    - Logistic Regression: "logistic regression using Col1, Col2, ..., ColN"
    - K-Means Clustering: "clustering using Col1, Col2, ..., ColN"
    - Principal Component Analysis (PCA): "pca using Col1, Col2, ..., ColN"
    - MANOVA: "manova using Col1, Col2, ..., ColN for ColX, ColY"

    Parameters:
    - input_string (str): A description of the analysis type and columns to use (e.g., "t-test on ColA and ColB").
    - df_string (str): A CSV-formatted string representing the data to be analyzed, which will be converted into a pandas DataFrame.

    Returns:
    - str: A summary of the statistical analysis, including results and column names used, or an error message if columns are missing or the analysis type is invalid.
    """
    
    # Convert the CSV string into a pandas DataFrame
    try:
        df = pd.read_csv(StringIO(df_string))
    except Exception as e:
        return f"Error parsing DataFrame from string: {e}"
    
    # Helper function to check if required columns exist in the DataFrame
    def check_columns(cols):
        missing_columns = [col for col in cols if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Helper function to extract columns from the input_string
    def extract_columns(pattern):
        import re
        columns = re.findall(r'on (\w+) and (\w+)', pattern)
        if columns:
            return columns[0]  # Returns a tuple (col1, col2)
        return None
    
    # T-test analysis
    def t_test_analysis(cols):
        check_columns(cols)
        results = []
        for i, row in df.iterrows():
            group1 = np.random.normal(loc=row[cols[0]], scale=5, size=100)
            group2 = np.random.normal(loc=row[cols[1]], scale=5, size=100)
            t_stat, p_value = ttest_ind(group1, group2)
            results.append(f"t-statistic: {t_stat:.2f}, p-value: {p_value:.4f}")
        return "\n".join(results)
    
    # Correlation analysis
    def correlation_analysis(cols):
        check_columns(cols)
        corr, p_value = pearsonr(df[cols[0]], df[cols[1]])
        return f"Correlation: {corr:.2f}, p-value: {p_value:.4f}"
    
    # ANOVA analysis
    def anova_analysis(cols):
        check_columns([cols[0], cols[1]])
        groups = [df[df[cols[1]] == group][cols[0]].values for group in df[cols[1]].unique()]
        f_stat, p_value = f_oneway(*groups)
        return f"ANOVA F-statistic: {f_stat:.2f}, p-value: {p_value:.4f}"
    
    # Linear regression analysis
    def linear_regression(cols):
        check_columns(cols)
        X = df[cols[:-1]]
        X = sm.add_constant(X)
        y = df[cols[-1]]
        model = sm.OLS(y, X).fit()
        return model.summary().as_text()
    
    # Chi-Square test
    def chi_square_test(cols):
        check_columns(cols)
        contingency_table = pd.crosstab(df[cols[0]], df[cols[1]])
        chi2, p, _, _ = chi2_contingency(contingency_table)
        return f"Chi-square statistic: {chi2:.2f}, p-value: {p:.4f}"
    
    # Logistic regression analysis
    def logistic_regression(cols):
        check_columns(cols)
        X = df[cols[:-1]]
        X = sm.add_constant(X)
        y = (df[cols[-1]] >= 500).astype(int)
        model = sm.Logit(y, X).fit()
        return model.summary().as_text()
    
    # K-Means clustering
    def kmeans_clustering(cols):
        check_columns(cols)
        kmeans = KMeans(n_clusters=3)
        df['Cluster'] = kmeans.fit_predict(df[cols])
        return df[['Country', 'Cluster']].to_string()
    
    # Principal Component Analysis (PCA)
    def pca_analysis(cols):
        check_columns(cols)
        pca = PCA(n_components=2)
        components = pca.fit_transform(df[cols])
        return pd.DataFrame(components, columns=['PC1', 'PC2']).to_string()
    
    # MANOVA analysis
    def manova_analysis(cols):
        check_columns(cols)
        X = df[cols[:-2]]
        y = df[cols[-2:]]
        manova = MANOVA(endog=y, exog=X)
        return manova.mv_test().summary()

    # Map input string to analysis function and parse columns
    analysis_mapping = {
        't-test': (t_test_analysis, 2),
        'correlation': (correlation_analysis, 2),
        'anova': (anova_analysis, 2),
        'linear regression': (linear_regression, 'multi'),
        'chi-square': (chi_square_test, 2),
        'logistic regression': (logistic_regression, 'multi'),
        'clustering': (kmeans_clustering, 'multi'),
        'pca': (pca_analysis, 'multi'),
        'manova': (manova_analysis, 'multi'),
    }
    
    # Find the relevant analysis based on input_string
    for analysis_type, (func, col_count) in analysis_mapping.items():
        if analysis_type in input_string.lower():
            if col_count == 2:
                # Extract 2 columns from input_string
                cols = extract_columns(input_string)
                if not cols:
                    return f"Error: Could not find the two required columns for {analysis_type} in the input string."
            else:
                # Handle the multi-column case (e.g., regression or clustering)
                cols = input_string.split("using ")[1].split(", ")
                check_columns(cols)
            
            return func(cols)
    
    return "No valid analysis type found in input_string."

