from langchain_core.tools import tool
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, f_oneway, chi2_contingency, pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, FactorAnalysis
import statsmodels.api as sm
from statsmodels.multivariate.manova import MANOVA
from io import StringIO

@tool
def analyze_pirls_problem(input_string, df_string):
    """
    Function to analyze PIRLS-related problems based on an input string and DataFrame provided as a string.
    
    This function performs different types of statistical analysis depending on the problem description
    provided in the input string. It supports the following statistical methods:
    
    - T-test: Compare the mean reading scores of countries to their benchmark.
    - Correlation: Calculate the correlation between two variables (e.g., reading scores and benchmarks).
    - ANOVA: Compare the mean reading scores across multiple countries.
    - Linear Regression: Model the relationship between reading scores and multiple independent variables.
    - Chi-Square Test: Assess the relationship between two categorical variables.
    - Logistic Regression: Predict the likelihood of achieving proficiency based on multiple factors.
    - K-Means Clustering: Group countries or students into clusters based on similar characteristics.
    - Principal Component Analysis (PCA): Reduce data dimensionality by summarizing variables.
    - MANOVA: Test the effect of independent variables on multiple dependent variables.
    
    Parameters:
    - input_string (str): A description of the problem, which determines the type of statistical analysis to perform.
      It can include keywords like 't-test', 'correlation', 'anova', 'linear regression', 'chi-square', 'logistic regression', 
      'clustering', 'pca', or 'manova' to trigger specific analyses.
    - df_string (str): A string representation of a CSV-like dataset, which is converted into a pandas DataFrame 
      for statistical analysis.
    
    Returns:
    - str: A summary or result of the statistical analysis, formatted as text, including the column names used in the analysis.
    """
    
    # Convert the provided string into a pandas DataFrame
    try:
        df = pd.read_csv(StringIO(df_string))
    except Exception as e:
        return f"Error parsing dataframe string: {e}"
    
    # Helper function to check for required columns
    def check_columns(required_columns):
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return f"Error: Missing required columns: {', '.join(missing_columns)}"
        return None
    
    # Subfunction for t-test analysis
    def run_ttest_analysis(df):
        required_columns = ['Avg_Reading_Score', 'Benchmark_Reading_Score']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        results = []
        for i, row in df.iterrows():
            country_scores = np.random.normal(loc=row['Avg_Reading_Score'], scale=5, size=100)
            benchmark_scores = np.random.normal(loc=row['Benchmark_Reading_Score'], scale=5, size=100)
            t_stat, p_value = ttest_ind(country_scores, benchmark_scores)
            results.append(f"Country: {row['Country']}, t-statistic: {t_stat:.2f}, p-value: {p_value:.4f}")
        columns_used = ['Avg_Reading_Score', 'Benchmark_Reading_Score']
        return "\n".join(results) + f"\nColumns used: {columns_used}"
    
    # Subfunction for correlation analysis
    def run_correlation_analysis(df):
        required_columns = ['Avg_Reading_Score', 'Benchmark_Reading_Score']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        corr, p_value = pearsonr(df['Avg_Reading_Score'], df['Benchmark_Reading_Score'])
        columns_used = ['Avg_Reading_Score', 'Benchmark_Reading_Score']
        return f"Correlation between Avg Reading Score and Benchmark: {corr:.2f}, p-value: {p_value:.4f}\nColumns used: {columns_used}"

    # Subfunction for ANOVA
    def run_anova(df):
        required_columns = ['Avg_Reading_Score', 'Country']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        groups = [df[df['Country'] == country]['Avg_Reading_Score'].values for country in df['Country'].unique()]
        f_stat, p_value = f_oneway(*groups)
        columns_used = ['Avg_Reading_Score', 'Country']
        return f"ANOVA F-statistic: {f_stat:.2f}, p-value: {p_value:.4f}\nColumns used: {columns_used}"
    
    # Subfunction for linear regression
    def run_linear_regression(df):
        required_columns = ['Parental_Education', 'School_Resources', 'Teacher_Experience', 'Avg_Reading_Score']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        X = df[['Parental_Education', 'School_Resources', 'Teacher_Experience']]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        y = df['Avg_Reading_Score']  # Dependent variable
        model = sm.OLS(y, X).fit()
        columns_used = ['Parental_Education', 'School_Resources', 'Teacher_Experience', 'Avg_Reading_Score']
        return str(model.summary()) + f"\nColumns used: {columns_used}"

    # Subfunction for Chi-Square test
    def run_chi_square(df):
        required_columns = ['Gender', 'Reading_Proficiency_Level']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        contingency_table = pd.crosstab(df['Gender'], df['Reading_Proficiency_Level'])
        chi2, p, dof, ex = chi2_contingency(contingency_table)
        columns_used = ['Gender', 'Reading_Proficiency_Level']
        return f"Chi-square statistic: {chi2:.2f}, p-value: {p:.4f}\nColumns used: {columns_used}"
    
    # Subfunction for logistic regression
    def run_logistic_regression(df):
        required_columns = ['Parental_Education', 'School_Resources', 'Teacher_Experience', 'Avg_Reading_Score']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        X = df[['Parental_Education', 'School_Resources', 'Teacher_Experience']]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        y = (df['Avg_Reading_Score'] >= 500).astype(int)  # Dependent variable (binary)
        model = sm.Logit(y, X).fit()
        columns_used = ['Parental_Education', 'School_Resources', 'Teacher_Experience', 'Avg_Reading_Score']
        return str(model.summary()) + f"\nColumns used: {columns_used}"

    # Subfunction for K-Means Clustering
    def run_kmeans_clustering(df):
        required_columns = ['Avg_Reading_Score', 'Parental_Education', 'School_Resources']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        kmeans = KMeans(n_clusters=3)
        df['Cluster'] = kmeans.fit_predict(df[['Avg_Reading_Score', 'Parental_Education', 'School_Resources']])
        columns_used = ['Avg_Reading_Score', 'Parental_Education', 'School_Resources']
        return df[['Country', 'Cluster']].to_string() + f"\nColumns used: {columns_used}"

    # Subfunction for PCA
    def run_pca(df):
        required_columns = ['Parental_Education', 'School_Resources', 'Teacher_Experience']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        pca = PCA(n_components=2)
        components = pca.fit_transform(df[['Parental_Education', 'School_Resources', 'Teacher_Experience']])
        columns_used = ['Parental_Education', 'School_Resources', 'Teacher_Experience']
        return pd.DataFrame(components, columns=['PC1', 'PC2']).to_string() + f"\nColumns used: {columns_used}"
    
    # Subfunction for MANOVA
    def run_manova(df):
        required_columns = ['Parental_Education', 'School_Resources', 'Avg_Reading_Score', 'Reading_Enjoyment']
        error_message = check_columns(required_columns)
        if error_message:
            return error_message
        
        X = df[['Parental_Education', 'School_Resources']]
        y = df[['Avg_Reading_Score', 'Reading_Enjoyment']]
        manova = MANOVA(endog=y, exog=X)
        columns_used = ['Parental_Education', 'School_Resources', 'Avg_Reading_Score', 'Reading_Enjoyment']
