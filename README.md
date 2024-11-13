# Capgemini Global Data Science Challenge 2024 README
Solution of the team "Backpropagating_since_4th_grade" - CIS Germany

## Table of contents
1. [Overview](#overview)
2. [Setup](#setup)
   1. [Repository Structure](#repository-structure)
   2. [Dependencies](#dependencies)
   3. [Usage](#usage)
   4. [Hardware & Performance](#hardware--performance)
3. [Methodology](#methodology)
   1. [Data](#data)
   2. [Model Description](#model-description)
   3. [Class Imbalance and Augmentations](#class-imbalance-and-augmentations)
   4. [Pre-trained vs. From Scratch](#pretrained-vs-trained-model)
   5. [Making Classifications](#making-classifications)
   6. [Model Evaluation](#model-evaluation)
4. [Disclaimer](#disclaimer)
5. [Contributors & Acknowledgements](#contributors--acknowledgements)
6. [Licenses](#licenses)


## Overview
This repository contains code to create an agentic system in LangGraph. The specific task was to equip policy-makers with a tool for guiding education interventions, ensuring decisions are based on accurate and actionable insights from PIRLS 2021. This README file provides an overview of the model, its functionality and how to use it. Refer to README files located in the sub-directories for in-depth explanation.  


## Setup

### Repository Structure
This is the expected structure to run the model successfully. 
Paths with no file ending are folders.

~~~
langgraph_testing/
  DS01_Langgraph_Guardrails.ipynb         Notebook for testing guardrails for code validation and SQL query validation.
  DS01_Langgraph_RAG for PDF and Web.ipynb         Notebook for testing RAG implementation with ChromaDB and HuggingFaceEmbeddings 
  DS01_Robust_Agent.ipynb         Notebook for testing extensive state management (against link and citation hallucination). 
  DS01_Minimal_Agent.ipynb         General notebook for established solution.
src/
  submission/  
    __init__.py    
    prompts/
      __init__.py
      system_prompt.py
    tools/
      __init__.py
      csv_handling.py         Code for handling of csvs and Excel
      data_viz.py         Code for plot generation (seaborn or quickchart)
      database.py         Code for database interaction
      pdf_handling.py         Code for PDF handling         
      stats_analysis.py         Code for statistical analysis, e.g. calculating Pearson correlation coefficient
      web_crawl.py         Code for web tools, e.g. DuckDuckGo search, Web Scraping, UIS data API
    create_submission.py         File for submission
requirements.txt
~~~


### Dependencies
External python libraries, frameworks, or packages that are required to run the model successfully. See also requirements.txt.

````
langgraph
setuptools==70.0.0
numpy==1.23.5
uvicorn==0.30.1
fastapi==0.110.3
python-dotenv==1.0.0
crewai==0.51.1
langchain==0.2.15
langchain-aws==0.1.17
sqlalchemy==2.0.31
tiktoken==0.7.0
pydantic==2.8.2
durationpy==0.6
async-timeout
psycopg2-binary==2.9.9
anthropic
openpyxl
seaborn
statsmodels
tabula-py
duckduckgo-search
torch==2.0.1
sentence-transformers
````


## Methodology

### Solutions for robustness
While a custom version of a ReAct architecture in LangGraph worked best for me regarding output quality and code simplicity, there were a few things that I tried out to stabilize the solution.
**State Management**
- results, links, decisions are captured in state to be used in later stages to reduce incentive for hallucinations (see DS01_Robust_Agent.ipynb)
**Response Validation**
- e.g. ensure only valid urls are shared, e.g. with custom is_valid_url function that checks whether a 200 response is returned (see DS01_Robust_Agent.ipynb, DS01_Langgraph_Guardrails.ipynb)
**Error Handling**
- for individual tools
- also for overall run method to ensure an answer is provided even if a server error occurs
**Output formatting for tools**
- reduce variance
**Few shot prompting**
- for SQL queries, but also for visualization code and final output
**Tool variety**
- Having a set of tools that can find a reply, even if query in one source doesn't succeed (e.g. UIS data API, Duckduckgo search, Web scraping, Excel and PDF reader)
