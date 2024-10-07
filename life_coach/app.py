import streamlit as st
import time
from langchain.retrievers import BM25Retriever


import transformers 
from transformers import pipeline
import pandas as pd
from tqdm.auto import tqdm

import ingest


from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
)


def print_log(message):
    print(message, flush=True)

# setup pipeline model
pipe = pipeline("text-generation",
        model="Qwen/Qwen2.5-0.5B", 
        device_map="auto",
        max_new_tokens=256,
        temperature=0.3,
       )


bm25_retriever = ingest.load_index()


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
    return {
        'answer': answer,
        'response_time': response_time,
        'model_used': 'Qwen/Qwen2.5-0.5B',
    }


def main():
    print_log("Starting Life Coach Assistant application")
    st.title("Life Coach")

    user_input = st.text_input("How Can help you?")

    
    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(
            f"New conversation started with ID: {st.session_state.conversation_id}"
        )
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")

    if st.button("Ask"):
        with st.spinner('Processing...'):
            output = rag(user_input)['answer']
            st.success("Completed!")
            st.write(output)

          # Save conversation to database
            print_log("Saving conversation to database")
            save_conversation(
                st.session_state.conversation_id, user_input, answer_data
            )
           
            st.session_state.conversation_id = str(uuid.uuid4())

     # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            st.session_state.count += 1
            print_log(
                f"Positive feedback received. New count: {st.session_state.count}"
            )
            save_feedback(st.session_state.conversation_id, 1)
            print_log("Positive feedback saved to database")
    with col2:
        if st.button("-1"):
            st.session_state.count -= 1
            print_log(
                f"Negative feedback received. New count: {st.session_state.count}"
            )
            save_feedback(st.session_state.conversation_id, -1)
            print_log("Negative feedback saved to database")

    st.write(f"Current count: {st.session_state.count}")

    # Display recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]
    )
    recent_conversations = get_recent_conversations(
        limit=5, relevance=relevance_filter if relevance_filter != "All" else None
    )
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevance: {conv['relevance']}")
        st.write(f"Model: {conv['model_used']}")
        st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

print_log("Streamlit app loop completed")

if __name__ == "__main__":
    main()