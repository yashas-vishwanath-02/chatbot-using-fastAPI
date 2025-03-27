import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/chatbot"  # Change this if using a deployed backend

st.set_page_config(page_title="Retail Chatbot", page_icon="🤖", layout="centered")

# Title and description
st.title("📱 Mobile Retail Chatbot")
st.write("Ask me anything about mobile phones, and I'll give you the best recommendations!")

# User input text box
user_query = st.text_input("Type your question here...", "")

if st.button("Ask Chatbot"):
    if user_query.strip() == "":
        st.warning("Please enter a question before clicking 'Ask Chatbot'.")
    else:
        # Send request to backend
        payload = {"customer_query": user_query}
        try:
            response = requests.post(API_URL, json=payload)
            response_data = response.json()

            # Display chatbot response
            if "response" in response_data:
                st.success(response_data["response"])
            else:
                st.error("Error: Unexpected response format.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")

# Feedback Section
st.subheader("💬 Provide Feedback")
feedback_query = st.text_input("What was your question?")
correct_response = st.text_area("What should have been the correct response?")

if st.button("Submit Feedback"):
    if not feedback_query or not correct_response:
        st.warning("Please fill out both fields before submitting feedback.")
    else:
        feedback_payload = {"customer_query": feedback_query, "correct_response": correct_response}
        try:
            feedback_response = requests.post("http://127.0.0.1:8000/feedback", json=feedback_payload)
            if feedback_response.status_code == 200:
                st.success("Feedback submitted successfully! Thank you for helping improve the chatbot.")
            else:
                st.error("Error submitting feedback.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")
