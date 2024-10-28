from langchain_core.tools import tool
import requests
import pypdf
import re
from sentence_transformers import SentenceTransformer, util
import os


@tool
def extract_top_paragraphs_from_url(pdf_url, user_input, top_n=2):
    """
    Downloads a PDF from a given URL, extracts text from it, splits the text into paragraphs,
    and returns the top N paragraphs most similar to the user input using Sentence-BERT.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        user_input (str): The input text to compare against the paragraphs in the PDF.
        top_n (int): The number of top similar paragraphs to return. Default is 2.

    Returns:
        list: A list of the top N paragraphs most similar to the user input, or a string with an error message if an exception occurs.
    """
    try:
        def download_pdf(url, output_path):
            """
            Downloads a PDF from a given URL and saves it to the specified output path.

            Args:
                url (str): The URL of the PDF file to download.
                output_path (str): The local file path to save the downloaded PDF.
            """
            response = requests.get(url)
            with open(output_path, 'wb') as file:
                file.write(response.content)

        def extract_text_from_pdf(pdf_path):
            """
            Extracts text from a PDF file.

            Args:
                pdf_path (str): The path to the PDF file.

            Returns:
                list: A list of strings, each representing the text of a page in the PDF.
            """
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                pages_text = []
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    pages_text.append(page.extract_text())
            return pages_text

        def split_into_paragraphs(text):
            """
            Splits text into paragraphs.

            Args:
                text (str): The text to split into paragraphs.

            Returns:
                list: A list of paragraphs.
            """
            paragraphs = text.split('\n\n')
            return [para.strip() for para in paragraphs if para.strip()]

        # Determine the local file name based on the URL
        pdf_filename = "downloaded.pdf"
        pdf_path = pdf_filename

        # Download the PDF
        download_pdf(pdf_url, pdf_path)

        # Extract text from the PDF
        pages_text = extract_text_from_pdf(pdf_path)

        # Split text into paragraphs
        all_paragraphs = []
        for page_text in pages_text:
            paragraphs = split_into_paragraphs(page_text)
            all_paragraphs.extend(paragraphs)

        # Load the Sentence-BERT model
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # Encode the paragraphs and the user input
        paragraph_embeddings = model.encode(all_paragraphs)
        user_input_embedding = model.encode([user_input])[0]

        # Compute cosine similarities
        similarities = util.pytorch_cos_sim(user_input_embedding, paragraph_embeddings)[0]
        top_indices = similarities.argsort(descending=True)[:top_n]

        # Get the top N paragraphs
        top_paragraphs = [all_paragraphs[i] for i in top_indices]

        return top_paragraphs

    except Exception as e:
        return f"An error occurred: {str(e)}"
    