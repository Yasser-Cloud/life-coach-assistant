import streamlit as st
import time
from langchain.retrievers import BM25Retriever


import transformers 
from transformers import pipeline
import pandas as pd
from tqdm.auto import tqdm

# setup pipeline model
pipe = pipeline("text-generation",
        model="Qwen/Qwen2.5-0.5B", 
        device_map="auto",
        max_new_tokens=256,
        temperature=0.3,
       )


bm25_retriever = BM25Retriever.from_documents(docs)


def sparse_search( query, k=10):

    # Perform sparse retrieval using BM25 (which may return only Document objects)
    sparse_docs = bm25_retriever.get_relevant_documents(query)
    
    # Assign a default score to the sparse results, e.g., BM25 doesn't return a score
    sparse_results = [(doc,1) for doc in sparse_docs]  # Assuming default score is 1.0
    
    
    return sparse_results

##     "content": "You are a professional life coach, offering personalized advice in different areas such as work, communication, hobbies, and lifestyle. It will provide suggestions to improve mood, recommend fun activities, and inspire productivity  ",


def build_prompt(query, search_results):
    prompt_template = """
    To answer QUESTION Use only the facts from the CONTEXT when answering the QUESTION.
    Read CONTEXT carefully to learn and give an accurate answer without hallucinations.
    In the CONTEXT you will have emojis and action help you to understand the text and use it.
    
    QUESTION: 
    '''{question}'''
    
    CONTEXT:
    '''{context}'''
    
    
    
    
    """.strip()
    
    entry_template = """
    emoji: {emoji}
    action: {action}
    dailog: {text}
    """.strip()

    
    context = ""
    
    for doc in search_results:
        context = context + entry_template.format(emoji = doc[0].metadata['emoji'],
                                                  action = doc[0].metadata['action'],
                                                  text = doc[0].page_content) +'\n\n'

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt):
    messages = [
    {"role"   : "system",
     "content": "You are a professional life coach, offering personalized advice in different areas such as work, communication, hobbies, and lifestyle. It will provide suggestions to improve mood, recommend fun activities, and inspire productivity. Answer the QUESTION based on the CONTEXT come from the user role. ",
      "role": "user", 
     "content": prompt,
   
    }
                ]
    return pipe(messages)[0]['generated_text'][1]['content']
    



def rag(query):
    search_results = sparse_search(query,3)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer


def main():
    st.title("RAG Function Invocation")

    user_input = st.text_input("Enter your input:")

    if st.button("Ask"):
        with st.spinner('Processing...'):
            output = rag(user_input)
            st.success("Completed!")
            st.write(output)

if __name__ == "__main__":
    main()