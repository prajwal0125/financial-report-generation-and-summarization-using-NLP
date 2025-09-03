import faiss
import numpy as np
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load financial data from a text file
file_path = "financial_data.txt"
with open(file_path, "r") as file:
    financial_text = file.read()

# Split text into chunks for efficient retrieval
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs = text_splitter.create_documents([financial_text])

# Embed documents using HuggingFace
embeddings = HuggingFaceEmbeddings()
vectors = [embeddings.embed_query(doc.page_content) for doc in docs]

# Create FAISS vector store
dimension = len(vectors[0])  # Get embedding size
index = faiss.IndexFlatL2(dimension)
index.add(np.array(vectors))

# Query the RAG system
query = "Provide a financial summary for Q4 2024"
query_vector = np.array(embeddings.embed_query(query)).reshape(1, -1)

# Retrieve top 3 relevant chunks
D, I = index.search(query_vector, k=3)
retrieved_text = "\n".join([docs[i].page_content for i in I[0]])

# Generate simple report from retrieved data
report = f"Q4 2024 Financial Summary:\n\n{retrieved_text}"

# Print the generated report
print(report)
