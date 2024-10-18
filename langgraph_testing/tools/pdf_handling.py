from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from pydantic import BaseModel

model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
hf_embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

# URL of the PDF document
pdf_url = "https://pirls2021.org/wp-content/uploads/2023/05/P21_MP_Ch3-sample-design.pdf"  # Replace with actual URL

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

generate_queries = (
    prompt_perspectives 
    | llm 
    | StrOutputParser() 
    | (lambda x: x.split("\n"))
)

class Config:
    arbitrary_types_allowed = True
    



