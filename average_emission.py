import json
import requests

url = "https://api.ourworldindata.org/v1/indicators/104780.metadata.json"
data_url = "https://api.ourworldindata.org/v1/indicators/104780.data.json"

# Make the GET request
try:
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON content
        metadata = response.json()
        print("Metadata fetched successfully!")
        
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
except requests.RequestException as e:
    print(f"An error occurred: {e}")

# Parse entities to create a dictionary mapping id to name
entities = metadata["dimensions"]["entities"]["values"]
id_to_name = {entity["id"]: entity["name"] for entity in entities}
categories = [entity["name"] for entity in entities]

# Make the GET request
try:
    response = requests.get(data_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON content
        data = response.json()
        print("data fetched successfully!")
        
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
except requests.RequestException as e:
    print(f"An error occurred: {e}")

# Create a mapping of entity ID to values, including names
entity_ids = data["entities"]
values = data["values"]

# Map entity ID to a dictionary containing its name and value
id_to_value = {entity_id: {"name": id_to_name.get(entity_id, "Unknown"), "value": value} 
               for entity_id, value in zip(entity_ids, values)}

## categories has a list of categories to classify products under
## id_to_value has a mapping of category name to value

# print(id_to_value)
