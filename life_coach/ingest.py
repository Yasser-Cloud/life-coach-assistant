import os
import pandas as pd
from langchain.schema import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import warnings

warnings.filterwarnings('ignore')

DATA_PATH =  os.getenv("DATA_PATH","../data/daily_dialog.csv")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
persist_directory = "../data/dialog_index"

def load_index(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    docs = [Document(page_content=row.text,metadata={'id':idx,'emoji':row.emoji,'action':row.action }) for idx ,row in df.iterrows()]
    #vectorstore = FAISS.from_documents(docs, embeddings)
    #vector_store = FAISS.load_local(embeddings,faiss_index_path)
    vectorstore = FAISS.load_local(persist_directory, embeddings, allow_dangerous_deserialization=True)


    bm25_retriever = BM25Retriever.from_documents(docs)

    return bm25_retriever, vectorstore