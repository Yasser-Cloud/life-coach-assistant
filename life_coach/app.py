import streamlit as st
import time
from langchain_community.retrievers import BM25Retriever

import transformers 
from transformers import pipeline
import pandas as pd

import ingest
import rag
import uuid
from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
)


def print_log(message):
    print(message, flush=True)




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
            output = rag.rag(user_input)
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
            # print_log(
            #     f"Positive feedback received. New count: {st.session_state.count}"
            # )
            # save_feedback(st.session_state.conversation_id, 1)
            # print_log("Positive feedback saved to database")
    with col2:
        if st.button("-1"):
            st.session_state.count -= 1
            print_log(
                f"Negative feedback received. New count: {st.session_state.count}"
            )
            save_feedback(st.session_state.conversation_id, -1)
            print_log("Negative feedback saved to database")
    st.write(f"Current count: {st.session_state.count}")

   

    

    print_log("Streamlit app loop completed")

if __name__ == "__main__":
    main()