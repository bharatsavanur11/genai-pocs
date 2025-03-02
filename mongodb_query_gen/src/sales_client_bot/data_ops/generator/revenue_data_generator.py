import json
import random
from datetime import datetime, timedelta
from bson import ObjectId

def generate_company_name():
    prefixes = ["Global", "Inter", "Trans", "Mega", "Alpha", "Beta", "Delta", "Omega", "Sigma", "Zenith"]
    suffixes = ["Capital", "Invest", "Finance", "Partners", "Holdings", "Group", "Ventures", "Assets", "Wealth", "Trust"]
    return f"{random.choice(prefixes)} {random.choice(suffixes)} Inc."

def generate_revenue_data(base_revenue):
    return {
        "equities": int(base_revenue * random.uniform(0.8, 1.2)),
        "derivatives": int(base_revenue * random.uniform(0.6, 1.0)),
        "prime_brokerage": int(base_revenue * random.uniform(0.4, 0.8))
    }

def generate_company_documents():
    documents = []
    regions = ["North America", "Europe", "Asia", "Global"]
    
    for company_id in range(1, 101):  # Generate 100 companies
        company_name = generate_company_name()
        client_id = f"GC{company_id:03d}"
        base_revenue = random.randint(1000000000, 5000000000)  # Base revenue between 1B and 5B
        
        for year in range(2015, 2025):
            for region in regions:
                revenue_data = generate_revenue_data(base_revenue)
                
                document = {
                    "_id": str(ObjectId()),
                    "company": company_name,
                    "client_id": client_id,
                    "client_name": company_name,
                    "currency": "USD",
                    "year": year,
                    "region": region,
                    "last_updated": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat(),
                    "equities": revenue_data["equities"],
                    "derivatives": revenue_data["derivatives"],
                    "prime_brokerage": revenue_data["prime_brokerage"]
                }
                
                documents.append(document)
            
            # Adjust base revenue for next year (simulating growth or decline)
            base_revenue *= random.uniform(0.95, 1.15)
    
    return documents

# Generate company documents
company_documents = generate_company_documents()

# Write to file
output_file = "/Users/bharatsavanur/Desktop/projects/agents/assignment_1/src/unbundled_company_revenue_data_2015_2024.json"
with open(output_file, "w") as f:
    json.dump(company_documents, f, indent=2)

print(f"Generated unbundled revenue data for 100 companies from 2015 to 2024. Data saved to {output_file}")