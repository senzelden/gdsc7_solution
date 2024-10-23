import requests
from io import BytesIO
from langchain_core.tools import tool
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from langchain.load import dumps, loads
from pydantic import BaseModel
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough


class Config:
    arbitrary_types_allowed = True

@tool
def create_agentic_system(question: str, pdf_url: str):
    """
    Process a question and retrieve relevant information from a PDF document using an agentic system.

    This function performs the following operations:
    
    1. **Load PDF Document**:
       - The function takes a URL pointing to a PDF document and loads it into memory.
       - The document is retrieved using a web request and loaded using the `PyPDFLoader`.

    2. **Document Metadata Addition**:
       - For each document, the PDF's source URL is added to the document's metadata. This metadata can be used later for traceability or to reference the source of the content.

    3. **Text Splitting**:
       - The loaded document is split into smaller chunks using `RecursiveCharacterTextSplitter`.
       - Each chunk has a maximum size of 300 characters, with a 50-character overlap between chunks to maintain context during retrieval.

    4. **Create Vector Store with Hugging Face Embeddings**:
       - The pre-initialized Hugging Face embeddings (`hf_embeddings`) are used to create a vector store for the split documents.
       - These embeddings are used to represent the text chunks as vectors, which allow for efficient similarity-based document retrieval.

    5. **Retrieve Relevant Document Chunks**:
       - A query is generated based on the input question. Multiple alternative versions of the query are generated using a language model (`ChatBedrock`) to account for different perspectives or ways to phrase the question.
       - These alternative queries help improve the relevance of the retrieved document chunks.
       - The documents are retrieved from the vector store based on the alternative queries, and a unique union of the retrieved documents is created to ensure no duplicates are included.

    6. **Retrieval-Augmented Generation (RAG) Chain**:
       - Once the relevant documents are retrieved, the context is used to answer the original question.
       - A prompt template is constructed to combine the retrieved document context and the original question.
       - This prompt is passed to a language model (`ChatBedrock`) to generate a final answer.

    Args:
        question (str): The input question provided by the user.
        pdf_url (str): The URL of the PDF document to be processed.

    Returns:
        str: The final answer generated based on the retrieved document context.
    
    Example usage:
        question = "What are the key findings in this report?"
        pdf_url = "https://pirls2021.org/bulgaria"
        
        answer = create_agentic_system(question, pdf_url, hf_embeddings)
        print(answer)
    """
    
    # Initialize Hugging Face embeddings once when the class is instantiated
    model_name = "BAAI/bge-large-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}

    hf_embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    try:
        # Load the PDF from the URL
        loader = PyPDFLoader(file_path=pdf_url)
        pdf_docs = loader.load()
    except requests.exceptions.RequestException as e:
        # Handle any network-related errors
        return f"Error: Failed to download the PDF. Details: {str(e)}"
    except Exception as e:
        # Handle errors in loading the PDF
        return f"Error: Unable to process the PDF document. Details: {str(e)}"

    try:
        # Add metadata (source) to each document
        for doc in pdf_docs:
            doc.metadata["source"] = pdf_url  # Add URL as the source

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=300,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(pdf_docs)

        # Use the pre-initialized vectorstore embeddings
        vectorstore = Chroma.from_documents(documents=splits, embedding=hf_embeddings)
        retriever = vectorstore.as_retriever()

        # Multi Query: Different Perspectives
        template = """You are an AI language model assistant. Your task is to generate three 
        different versions of the given user question to retrieve relevant documents from a vector 
        database. Provide these alternative questions separated by newlines. 
        Original question: {question}"""
        prompt_perspectives = ChatPromptTemplate.from_template(template)

        generate_queries = (
            prompt_perspectives
            | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
            | StrOutputParser()
            | (lambda x: x.split("\n"))
        )

        def get_unique_union(documents: list[list]):
            """ Unique union of retrieved docs """
            flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
            unique_docs = list(set(flattened_docs))
            return [loads(doc) for doc in unique_docs]

        # Retrieve
        retrieval_chain = generate_queries | retriever.map() | get_unique_union
        docs = retrieval_chain.invoke({"question": question})

        # RAG Chain
        template = """Answer the following question based on this context:

        {context}

        Question: {question}

        Answer:
        """

        prompt = ChatPromptTemplate.from_template(template)

        final_rag_chain = (
            {"context": retrieval_chain, "question": itemgetter("question")}
            | prompt
            | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
            | StrOutputParser()
        )

        return final_rag_chain.invoke({"question": question})

    except Exception as e:
        # Catch any errors in document processing, retrieval, or RAG generation
        return f"Error: An issue occurred during processing. Details: {str(e)}"
