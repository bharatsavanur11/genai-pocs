import json
from collections import defaultdict

def load_json_data(file_path):
    """Load JSON data from the given file path."""
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_unique_clients(data):
    """Extract unique client_ids and client_names from the data."""
    unique_clients = defaultdict(set)
    for entry in data:
        client_id = entry.get('client_id')
        client_name = entry.get('client_name')
        if client_id and client_name:
            unique_clients[client_id].add(client_name)
    
    # Convert the defaultdict to a JSON-compatible dictionary
    json_dict = {
        client_id: next(iter(names)) if names else ""
        for client_id, names in unique_clients.items()
    }
    
    return json_dict

def write_unique_clients_to_json(unique_clients, output_file):
    """Write the unique clients data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(unique_clients, f, indent=2)
    print(f"Unique client data has been written to {output_file}")

def main():
    input_file = "/Users/bharatsavanur/Desktop/projects/agents/assignment_1/src/sales_client_bot/data_ops/data/revenue_data.json"
    output_file = "/Users/bharatsavanur/Desktop/projects/agents/assignment_1/src/sales_client_bot/data_ops/data/client_data.json"
    
    data = load_json_data(input_file)
    unique_clients = extract_unique_clients(data)
    write_unique_clients_to_json(unique_clients, output_file)

if __name__ == "__main__":
    main()