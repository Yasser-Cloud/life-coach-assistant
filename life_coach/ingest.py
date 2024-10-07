import os
import pandas as pd
from langchain.schema import Document
from langchain.retrievers import BM25Retriever

DATA_PATH =  os.getenv("DATA_PATH","../data/daily_dialog.csv")

def load_index(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    docs = [Document(page_content=row.text,metadata={'id':idx,'emoji':row.emoji,'action':row.action }) for idx ,row in df.iterrows()]


    bm25_retriever = BM25Retriever.from_documents(docs)

    return bm25_retriever