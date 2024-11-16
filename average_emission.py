# categories.py
from fastapi import APIRouter
import requests
from sklearn.cluster import KMeans
import numpy as np

router = APIRouter()

metadata_url = "https://api.ourworldindata.org/v1/indicators/104780.metadata.json"
data_url = "https://api.ourworldindata.org/v1/indicators/104780.data.json"

# Helper to fetch metadata
def fetch_metadata():
    response = requests.get(metadata_url)
    response.raise_for_status()
    metadata = response.json()
    entities = metadata["dimensions"]["entities"]["values"]
    id_to_name = {entity["id"]: entity["name"] for entity in entities}
    return id_to_name

# Helper to fetch data
def fetch_data():
    response = requests.get(data_url)
    response.raise_for_status()
    data = response.json()
    return data

# Endpoint to fetch categories
@router.get("/categories")
async def get_categories():
    id_to_name = fetch_metadata()
    categories = sorted(id_to_name.values())  # Sorted by category names
    return {"categories": categories}

# Endpoint to fetch weights for a specific category
@router.get("/footprint-info/{category_name}")
async def get_info(category_name: str):
    id_to_name = fetch_metadata()
    data = fetch_data()

    # Map entity ID to name and value
    entity_ids = data["entities"]
    values = data["values"]
    id_to_value = {entity_id: {"name": id_to_name.get(entity_id, "Unknown"), "value": value} 
                   for entity_id, value in zip(entity_ids, values)}

    # Sort by category name and find Rice
    sorted_categories = sorted(id_to_value.values(), key=lambda x: x["value"])
    rice_entry = next((entry for entry in sorted_categories if entry["name"] == "Rice"), None)

    if not rice_entry:
        return {"error": "Rice category not found."}

    # Group up to "Rice" into subsets using KMeans clustering
    rice_index = sorted_categories.index(rice_entry)
    subset_data = sorted_categories[:rice_index + 1]
    values_to_cluster = np.array([entry["value"] for entry in subset_data]).reshape(-1, 1)

    # Perform clustering
    num_clusters = 5  # Adjust as needed
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(values_to_cluster)

    # Assign weights based on clusters
    cluster_to_weight = {cluster: (num_clusters - i) * 10 for i, cluster in enumerate(sorted(set(cluster_labels)))}
    for i, entry in enumerate(subset_data):
        # entry["cluster"] = cluster_labels[i]
        entry["assigned_weight"] = cluster_to_weight[cluster_labels[i]]

    category = next((entry for entry in subset_data if entry["name"].lower() == category_name.lower()), None)

    if category:
        # Return the details of the specific category
        return {
            "category": category["name"],
            "value": category["value"],
            "assigned_weight": category["assigned_weight"]
        }
    else:
        return {
            "category": category["name"],
            "value": 0,
            "assigned_weight": 0
        }