# import pickle
# import requests
# from io import BytesIO
from langchain_core.tools import tool
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# from langchain.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_core.output_parsers import StrOutputParser
# from langchain.prompts import ChatPromptTemplate
# from langchain_aws import ChatBedrock
# from langchain.load import dumps, loads
# from pydantic import BaseModel
# from operator import itemgetter
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.runnables import RunnableConfig
# from langchain_core.tools import InjectedToolArg
# from langgraph.store.base import BaseStore
# from typing import Annotated
# from langgraph.prebuilt import InjectedState, InjectedStore
# import langchain_community
import requests
import pypdf
import re
from sentence_transformers import SentenceTransformer, util
import os




# class Config:
#     arbitrary_types_allowed = True

# @tool
# def create_agentic_system(question: str, pdf_url: str, embeddings: Annotated[langchain_community.embeddings.huggingface.HuggingFaceBgeEmbeddings
# , InjectedState("embeddings")]):
#     """
#     Process a question and retrieve relevant information from a PDF document using an agentic system.

#     This function performs the following operations:
    
#     1. **Load PDF Document**:
#        - The function takes a URL pointing to a PDF document and loads it into memory.
#        - The document is retrieved using a web request and loaded using the `PyPDFLoader`.

#     2. **Document Metadata Addition**:
#        - For each document, the PDF's source URL is added to the document's metadata. This metadata can be used later for traceability or to reference the source of the content.

#     3. **Text Splitting**:
#        - The loaded document is split into smaller chunks using `RecursiveCharacterTextSplitter`.
#        - Each chunk has a maximum size of 300 characters, with a 50-character overlap between chunks to maintain context during retrieval.

#     4. **Create Vector Store with Hugging Face Embeddings**:
#        - The pre-initialized Hugging Face embeddings (`hf_embeddings`) are used to create a vector store for the split documents.
#        - These embeddings are used to represent the text chunks as vectors, which allow for efficient similarity-based document retrieval.

#     5. **Retrieve Relevant Document Chunks**:
#        - A query is generated based on the input question. Multiple alternative versions of the query are generated using a language model (`ChatBedrock`) to account for different perspectives or ways to phrase the question.
#        - These alternative queries help improve the relevance of the retrieved document chunks.
#        - The documents are retrieved from the vector store based on the alternative queries, and a unique union of the retrieved documents is created to ensure no duplicates are included.

#     6. **Retrieval-Augmented Generation (RAG) Chain**:
#        - Once the relevant documents are retrieved, the context is used to answer the original question.
#        - A prompt template is constructed to combine the retrieved document context and the original question.
#        - This prompt is passed to a language model (`ChatBedrock`) to generate a final answer.

#     Args:
#         question (str): The input question provided by the user.
#         pdf_url (str): The URL of the PDF document to be processed.

#     Returns:
#         str: The final answer generated based on the retrieved document context.
    
#     Example usage:
#         question = "What are the key findings in this report?"
#         pdf_url = "https://pirls2021.org/bulgaria"
        
#         answer = create_agentic_system(question, pdf_url, hf_embeddings)
#         print(answer)
#     """
    
#     # Initialize Hugging Face embeddings once when the class is instantiated
# #     model_name = "BAAI/bge-large-en-v1.5"
# #     model_kwargs = {'device': 'cpu'}
# #     encode_kwargs = {'normalize_embeddings': True}

# #     hf_embeddings = HuggingFaceBgeEmbeddings(
# #         model_name=model_name,
# #         model_kwargs=model_kwargs,
# #         encode_kwargs=encode_kwargs
# #     )
#     hf_embeddings = embeddings
    
#     try:
#         # Load the PDF from the URL
#         loader = PyPDFLoader(file_path=pdf_url)
#         pdf_docs = loader.load()
#     except requests.exceptions.RequestException as e:
#         # Handle any network-related errors
#         return f"Error: Failed to download the PDF. Details: {str(e)}"
#     except Exception as e:
#         # Handle errors in loading the PDF
#         return f"Error: Unable to process the PDF document. Details: {str(e)}"

#     try:
#         # Add metadata (source) to each document
#         for doc in pdf_docs:
#             doc.metadata["source"] = pdf_url  # Add URL as the source

#         # Split the document into chunks
#         text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#             chunk_size=300,
#             chunk_overlap=50
#         )
#         splits = text_splitter.split_documents(pdf_docs)

#         # Use the pre-initialized vectorstore embeddings
#         vectorstore = Chroma.from_documents(documents=splits, embedding=hf_embeddings)
#         retriever = vectorstore.as_retriever()

#         # Multi Query: Different Perspectives
#         template = """You are an AI language model assistant. Your task is to generate three 
#         different versions of the given user question to retrieve relevant documents from a vector 
#         database. Provide these alternative questions separated by newlines. 
#         Original question: {question}"""
#         prompt_perspectives = ChatPromptTemplate.from_template(template)

#         generate_queries = (
#             prompt_perspectives
#             | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
#             | StrOutputParser()
#             | (lambda x: x.split("\n"))
#         )

#         def get_unique_union(documents: list[list]):
#             """ Unique union of retrieved docs """
#             flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
#             unique_docs = list(set(flattened_docs))
#             return [loads(doc) for doc in unique_docs]

#         # Retrieve
#         retrieval_chain = generate_queries | retriever.map() | get_unique_union
#         docs = retrieval_chain.invoke({"question": question})

#         # RAG Chain
#         template = """Answer the following question based on this context:

#         {context}

#         Question: {question}

#         Answer:
#         """

#         prompt = ChatPromptTemplate.from_template(template)

#         final_rag_chain = (
#             {"context": retrieval_chain, "question": itemgetter("question")}
#             | prompt
#             | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
#             | StrOutputParser()
#         )

#         return final_rag_chain.invoke({"question": question})

#     except Exception as e:
#         # Catch any errors in document processing, retrieval, or RAG generation
#         return f"Error: An issue occurred during processing. Details: {str(e)}"

# @tool
# def retrieve_from_pickle(pkl_file_name: str, question: str) -> str:
#     """
#     Retrieves relevant documents from a pickled vectorstore and generates an answer to a given question.
    
#     This function first loads documents and embeddings from a specified pickle file, recreates a vectorstore 
#     using the loaded data, and then retrieves relevant documents based on a user-provided question. The function 
#     generates three alternative versions of the user’s question, retrieves the documents, and returns an AI-generated 
#     response based on the retrieved documents using a RAG (Retrieval-Augmented Generation) approach.

#     If any errors occur during the process, the function returns a descriptive error message.

#     Parameters:
#     ----------
#     pkl_file_name : str
#         The name of the pickle file that contains the documents and their embeddings.
        
#     question : str
#         The question posed by the user to retrieve relevant documents and generate an answer.
        
#     Returns:
#     -------
#     str
#         The final generated answer from the retrieved documents in response to the user's question,
#         or an error message if the process fails.
#     """

#     try:
#         # Initialize Hugging Face embeddings once when the class is instantiated
#         model_name = "BAAI/bge-large-en-v1.5"
#         model_kwargs = {'device': 'cpu'}
#         encode_kwargs = {'normalize_embeddings': True}

#         hf_embeddings = HuggingFaceBgeEmbeddings(
#             model_name=model_name,
#             model_kwargs=model_kwargs,
#             encode_kwargs=encode_kwargs
#         )
        
#         # Load the pickled documents and embeddings
#         with open(pkl_file_name, "rb") as f:
#             data = pickle.load(f)

#         documents = data["documents"]

#         # Recreate the vectorstore from the loaded documents
#         vectorstore = Chroma.from_documents(documents=documents, embedding=hf_embeddings)

#         # Use the vectorstore retriever
#         retriever = vectorstore.as_retriever()

#         # Multi Query: Different Perspectives
#         template = """You are an AI language model assistant. Your task is to generate three 
#         different versions of the given user question to retrieve relevant documents from a vector 
#         database. Provide these alternative questions separated by newlines. 
#         Original question: {question}"""
        
#         prompt_perspectives = ChatPromptTemplate.from_template(template)

#         generate_queries = (
#             prompt_perspectives
#             | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
#             | StrOutputParser()
#             | (lambda x: x.split("\n"))
#         )

#         def get_unique_union(documents: list[list]):
#             """Unique union of retrieved docs"""
#             flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
#             unique_docs = list(set(flattened_docs))
#             return [loads(doc) for doc in unique_docs]

#         # Generate queries based on the original question
#         queries = generate_queries.invoke({"question": question})

#         # Retrieve documents for each query
#         retrieved_docs = []
#         for query in queries:
#             retrieved_docs.append(retriever.get_relevant_documents(query))

#         # Get a unique set of retrieved documents
#         docs = get_unique_union(retrieved_docs)

#         # RAG Chain to generate the final answer
#         rag_template = """Answer the following question based on this context:

#         {context}

#         Question: {question}

#         Please always provide direct citations in your summary, but don't mention the source.

#         Answer:
#         """
        
#         prompt = ChatPromptTemplate.from_template(rag_template)

#         final_rag_chain = (
#             {"context": docs, "question": question}
#             | prompt
#             | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
#             | StrOutputParser()
#         )

#         # Return the final answer from the RAG chain
#         return final_rag_chain.invoke({"question": question})

#     except Exception as e:
#         # Return a string describing the error
#         return f"An error occurred: {str(e)}"


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
