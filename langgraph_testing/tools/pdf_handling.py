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
    Create an agentic system to process a question and retrieve relevant information from a PDF document.

    This function performs the following steps:
    1. Loads a PDF document from a specified URL.
    2. Splits the document into smaller chunks for processing.
    3. Creates a vector store using Hugging Face embeddings.
    4. Generates multiple perspectives of the input question to improve retrieval accuracy.
    5. Retrieves relevant document chunks based on the generated questions.
    6. Uses a Retrieval-Augmented Generation (RAG) chain to generate a final answer based on the retrieved context.

    Args:
        question (str): The input question to be processed.
        pdf_url (str): The URL of the PDF document to load.

    Returns:
        str: The generated answer based on the retrieved context.

    Example usage:
        question = "What is this?"
        pdf_url = "https://example.com/document.pdf"
        response = create_agentic_system(question, pdf_url)
        print(response)
    """
    
    model_name = "BAAI/bge-large-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    hf_embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # Load the PDF from the URL
    loader = PyPDFLoader(file_path=pdf_url)
    pdf_docs = loader.load()

    # Add metadata (source) to each document
    for doc in pdf_docs:
        doc.metadata["source"] = pdf_url  # Add URL as the source

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(pdf_docs)

    # Create the vectorstore using Hugging Face embeddings and IDs
    vectorstore = Chroma.from_documents(documents=splits, 
                                        embedding=hf_embeddings)

    retriever = vectorstore.as_retriever()

    # Multi Query: Different Perspectives
    template = """You are an AI language model assistant. Your task is to generate three 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    generate_queries = (
        prompt_perspectives 
        | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192}) 
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )

    def get_unique_union(documents: list[list]):
        """ Unique union of retrieved docs """
        # Flatten list of lists, and convert each Document to string
        flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
        # Get unique documents
        unique_docs = list(set(flattened_docs))
        # Return
        return [loads(doc) for doc in unique_docs]

    # Retrieve
    retrieval_chain = generate_queries | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question": question})

    # RAG
    template = """Answer the following question based on this context:

    {context}

    Question: {question}

    Answer:
    """

    prompt = ChatPromptTemplate.from_template(template)

    final_rag_chain = (
        {"context": retrieval_chain, 
         "question": itemgetter("question")} 
        | prompt
        | ChatBedrock(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", model_kwargs={'temperature': 0, "max_tokens": 8192})
        | StrOutputParser()
    )

    return final_rag_chain.invoke({"question": question})
