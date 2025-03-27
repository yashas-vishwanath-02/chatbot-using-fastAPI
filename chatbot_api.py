import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.preprocessing import preprocess_text  # Import preprocessing function

# Initialize FastAPI with metadata
app = FastAPI(
    title="Retail Chatbot API",
    description="An NLP-powered chatbot for mobile phone recommendations.",
    version="1.0.0"
)

# Hugging Face API Key (Replace with your own)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
# Headers for Hugging Face API
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Hugging Face Model URL
HF_MODEL_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

# Load fine-tuned data from JSON file
DATA_FILE = "data/customer_queries.json"

def load_fine_tuned_data():
    """Loads fine-tuned customer queries dataset."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # If file doesn't exist, return an empty list

def save_fine_tuned_data(data):
    """Saves updated fine-tuned dataset."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Load dataset into memory
fine_tuned_data = load_fine_tuned_data()

# Define request models
class Query(BaseModel):
    customer_query: str

class Feedback(BaseModel):
    customer_query: str
    correct_response: str

@app.post("/chatbot", summary="Get chatbot response", response_description="Generated chatbot response")
async def chatbot(query: Query):
    """
    Processes a customer's query and returns a smartphone recommendation.

    - **customer_query**: The input query from the user.
    - **Response**: Returns the chatbot-generated response.
    """
    try:
        if not query.customer_query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # Preprocess the customer query
        cleaned_query = preprocess_text(query.customer_query)

        # Check fine-tuned dataset first
        for entry in fine_tuned_data:
            if cleaned_query in preprocess_text(entry["customer_query"]):
                return {"response": entry["response"]}

        # If no match, fallback to Hugging Face API
        prompt = f"You are a mobile expert chatbot. A customer asks: '{cleaned_query}'. Provide the best recommendations."
        data = {"inputs": prompt, "wait_for_model": True}

        response = requests.post(HF_MODEL_URL, headers=headers, json=data)
        response_data = response.json()

        if isinstance(response_data, list) and "generated_text" in response_data[0]:
            return {"response": response_data[0]["generated_text"]}
        elif "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data["error"])
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format.")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to external API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/feedback", summary="Submit feedback", response_description="Updates chatbot with correct response")
async def feedback(feedback: Feedback):
    """
    Allows users to submit feedback to improve chatbot responses.

    - **customer_query**: The user's original query.
    - **correct_response**: The correct response the chatbot should provide.
    - **Response**: Acknowledgment message.
    """
    try:
        if not feedback.customer_query.strip() or not feedback.correct_response.strip():
            raise HTTPException(status_code=400, detail="Both customer_query and correct_response are required.")

        # Preprocess the customer query
        cleaned_query = preprocess_text(feedback.customer_query)

        # Check if query already exists in the dataset
        for entry in fine_tuned_data:
            if cleaned_query in preprocess_text(entry["customer_query"]):
                entry["response"] = feedback.correct_response  # Update response
                save_fine_tuned_data(fine_tuned_data)
                return {"message": "Response updated successfully"}

        # If new query, add to dataset
        fine_tuned_data.append({"customer_query": feedback.customer_query, "response": feedback.correct_response})
        save_fine_tuned_data(fine_tuned_data)

        return {"message": "New query added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/", summary="API Root", response_description="Welcome message")
async def root():
    """
    API Root Endpoint.

    - **Response**: Returns a simple welcome message.
    """
    return {"message": "Welcome to the Retail Chatbot API! Use /docs for API documentation."}
