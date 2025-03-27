import json
import random
from utils.preprocessing import preprocess_text

# Load the dataset
with open("data/customer_queries.json", "r") as file:
    dataset = json.load(file)

# Simulating fine-tuning by preprocessing the dataset
processed_dataset = [
    {
        "customer_query": preprocess_text(entry["customer_query"]),
        "response": entry["response"]
    }
    for entry in dataset
]

# Save the processed data for future use
with open("training/fine_tuned_data.json", "w") as file:
    json.dump(processed_dataset, file, indent=4)

print("Fine-tuning process completed. Preprocessed data saved.")
