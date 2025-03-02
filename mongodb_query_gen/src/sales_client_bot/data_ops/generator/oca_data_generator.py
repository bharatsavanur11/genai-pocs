import json
import random
import os
# List of clients
clients = [
    {"clientID": "GC001", "clientName": "Delta Trust Inc."},
    {"clientID": "GC002", "clientName": "Sigma Invest Inc."},
    {"clientID": "GC003", "clientName": "Inter Wealth Inc."},
    {"clientID": "GC004", "clientName": "Global Wealth Inc."},
    {"clientID": "GC005", "clientName": "Trans Trust Inc."},
    {"clientID": "GC006", "clientName": "Trans Group Inc."},
    {"clientID": "GC007", "clientName": "Alpha Wealth Inc."},
    {"clientID": "GC008", "clientName": "Mega Invest Inc."},
    {"clientID": "GC009", "clientName": "Global Invest Inc."},
    {"clientID": "GC010", "clientName": "Inter Assets Inc."},
    {"clientID": "GC011", "clientName": "Sigma Trust Inc."},
    {"clientID": "GC012", "clientName": "Global Trust Inc."},
    {"clientID": "GC013", "clientName": "Alpha Holdings Inc."},
    {"clientID": "GC014", "clientName": "Delta Invest Inc."},
    {"clientID": "GC015", "clientName": "Global Group Inc."},
    {"clientID": "GC016", "clientName": "Inter Wealth Inc."},
    {"clientID": "GC017", "clientName": "Alpha Ventures Inc."},
    {"clientID": "GC018", "clientName": "Trans Finance Inc."},
    {"clientID": "GC019", "clientName": "Global Wealth Inc."},
    {"clientID": "GC020", "clientName": "Trans Group Inc."},
    {"clientID": "GC021", "clientName": "Sigma Holdings Inc."},
    {"clientID": "GC022", "clientName": "Inter Group Inc."},
    {"clientID": "GC023", "clientName": "Beta Ventures Inc."},
    {"clientID": "GC024", "clientName": "Inter Holdings Inc."},
    {"clientID": "GC025", "clientName": "Sigma Capital Inc."},
    {"clientID": "GC026", "clientName": "Beta Finance Inc."},
    {"clientID": "GC027", "clientName": "Trans Capital Inc."},
    {"clientID": "GC028", "clientName": "Sigma Capital Inc."},
    {"clientID": "GC029", "clientName": "Delta Invest Inc."},
    {"clientID": "GC030", "clientName": "Trans Assets Inc."},
    {"clientID": "GC031", "clientName": "Beta Assets Inc."},
    {"clientID": "GC032", "clientName": "Omega Capital Inc."},
    {"clientID": "GC033", "clientName": "Trans Partners Inc."},
    {"clientID": "GC034", "clientName": "Inter Assets Inc."},
    {"clientID": "GC035", "clientName": "Global Ventures Inc."},
    {"clientID": "GC036", "clientName": "Global Assets Inc."},
    {"clientID": "GC037", "clientName": "Omega Ventures Inc."},
    {"clientID": "GC038", "clientName": "Global Trust Inc."},
    {"clientID": "GC039", "clientName": "Mega Finance Inc."},
    {"clientID": "GC040", "clientName": "Beta Capital Inc."},
    {"clientID": "GC041", "clientName": "Trans Assets Inc."},
    {"clientID": "GC042", "clientName": "Global Partners Inc."},
    {"clientID": "GC043", "clientName": "Alpha Ventures Inc."},
    {"clientID": "GC044", "clientName": "Delta Partners Inc."},
    {"clientID": "GC045", "clientName": "Beta Ventures Inc."},
    {"clientID": "GC046", "clientName": "Mega Assets Inc."},
    {"clientID": "GC047", "clientName": "Beta Holdings Inc."},
    {"clientID": "GC048", "clientName": "Trans Invest Inc."},
    {"clientID": "GC049", "clientName": "Trans Capital Inc."},
    {"clientID": "GC050", "clientName": "Omega Wealth Inc."},
    {"clientID": "GC051", "clientName": "Zenith Holdings Inc."},
    {"clientID": "GC052", "clientName": "Mega Finance Inc."},
    {"clientID": "GC053", "clientName": "Delta Ventures Inc."},
    {"clientID": "GC054", "clientName": "Delta Wealth Inc."},
    {"clientID": "GC055", "clientName": "Zenith Holdings Inc."},
    {"clientID": "GC056", "clientName": "Zenith Trust Inc."},
    {"clientID": "GC057", "clientName": "Omega Finance Inc."},
    {"clientID": "GC058", "clientName": "Global Finance Inc."},
    {"clientID": "GC059", "clientName": "Beta Capital Inc."},
    {"clientID": "GC060", "clientName": "Omega Ventures Inc."},
    {"clientID": "GC061", "clientName": "Omega Group Inc."},
    {"clientID": "GC062", "clientName": "Beta Ventures Inc."},
    {"clientID": "GC063", "clientName": "Trans Assets Inc."},
    {"clientID": "GC064", "clientName": "Inter Finance Inc."},
    {"clientID": "GC065", "clientName": "Alpha Holdings Inc."},
    {"clientID": "GC066", "clientName": "Beta Invest Inc."},
    {"clientID": "GC067", "clientName": "Trans Partners Inc."},
    {"clientID": "GC068", "clientName": "Zenith Assets Inc."},
    {"clientID": "GC069", "clientName": "Trans Partners Inc."},
    {"clientID": "GC070", "clientName": "Beta Ventures Inc."},
    {"clientID": "GC071", "clientName": "Omega Invest Inc."},
    {"clientID": "GC072", "clientName": "Omega Ventures Inc."},
    {"clientID": "GC073", "clientName": "Zenith Holdings Inc."},
    {"clientID": "GC074", "clientName": "Omega Wealth Inc."},
    {"clientID": "GC075", "clientName": "Mega Invest Inc."},
    {"clientID": "GC076", "clientName": "Global Assets Inc."},
    {"clientID": "GC077", "clientName": "Global Finance Inc."},
    {"clientID": "GC078", "clientName": "Omega Invest Inc."},
    {"clientID": "GC079", "clientName": "Global Wealth Inc."},
    {"clientID": "GC080", "clientName": "Mega Capital Inc."},
    {"clientID": "GC081", "clientName": "Sigma Assets Inc."},
    {"clientID": "GC082", "clientName": "Zenith Group Inc."},
    {"clientID": "GC083", "clientName": "Trans Finance Inc."},
    {"clientID": "GC084", "clientName": "Sigma Invest Inc."},
    {"clientID": "GC085", "clientName": "Global Trust Inc."},
    {"clientID": "GC086", "clientName": "Alpha Assets Inc."},
    {"clientID": "GC087", "clientName": "Sigma Capital Inc."},
    {"clientID": "GC088", "clientName": "Mega Trust Inc."},
    {"clientID": "GC089", "clientName": "Sigma Holdings Inc."},
    {"clientID": "GC090", "clientName": "Sigma Capital Inc."},
    {"clientID": "GC091", "clientName": "Mega Holdings Inc."},
    {"clientID": "GC092", "clientName": "Inter Group Inc."},
    {"clientID": "GC093", "clientName": "Sigma Assets Inc."},
    {"clientID": "GC094", "clientName": "Sigma Finance Inc."},
    {"clientID": "GC095", "clientName": "Sigma Holdings Inc."},
    {"clientID": "GC096", "clientName": "Delta Wealth Inc."},
    {"clientID": "GC097", "clientName": "Delta Invest Inc."},
    {"clientID": "GC098", "clientName": "Sigma Partners Inc."},
    {"clientID": "GC099", "clientName": "Global Capital Inc."},
    {"clientID": "GC100", "clientName": "Delta Group Inc."}
]

# Lists of potential opportunities, challenges, and action items
opportunities = [
    "Expand into emerging markets",
    "Develop AI-powered financial solutions",
    "Launch sustainable investment products",
    "Implement blockchain technology",
    "Introduce robo-advisory services",
    "Expand alternative investment offerings",
    "Develop cross-border investment solutions",
    "Launch digital wealth management platform",
    "Introduce personalized financial planning tools",
    "Expand into impact investing"
]

challenges = [
    "Adapting to changing regulations",
    "Managing cybersecurity risks",
    "Navigating market volatility",
    "Addressing talent acquisition and retention",
    "Keeping pace with technological advancements",
    "Managing client expectations in low-yield environments",
    "Dealing with increased competition",
    "Ensuring data privacy and compliance",
    "Adapting to shifting demographics",
    "Maintaining operational efficiency"
]

action_items = [
    "Conduct market research and feasibility study",
    "Implement advanced security protocols",
    "Develop comprehensive risk management strategy",
    "Create innovative employee development programs",
    "Establish partnerships with fintech companies",
    "Implement AI-driven portfolio optimization",
    "Conduct comprehensive digital transformation",
    "Develop targeted marketing campaigns",
    "Enhance client communication channels",
    "Streamline operational processes"
]

def generate_entry(client, entry_type, content):
    return {
        "clientID": client["clientID"],
        "clientName": client["clientName"],
        entry_type: content
    }

def generate_client_data(client):
    client_data = []
    for _ in range(3):
        client_data.append(generate_entry(client, "Opportunity", random.choice(opportunities)))
        client_data.append(generate_entry(client, "Challenge", random.choice(challenges)))
        client_data.append(generate_entry(client, "ActionItem", random.choice(action_items)))
    return client_data

def main():
    all_data = []
    for client in clients:
        all_data.extend(generate_client_data(client))
    
    # Define the output directory and file name
    output_dir = "/Users/bharatsavanur/Desktop/projects/agents/assignment_1/src/sales_client_bot/data_ops/data"
    output_file = "client_opportunities_challenges_actions.json"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write to JSON file
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"Data generation complete. Check '{output_path}'")

if __name__ == "__main__":
    main()