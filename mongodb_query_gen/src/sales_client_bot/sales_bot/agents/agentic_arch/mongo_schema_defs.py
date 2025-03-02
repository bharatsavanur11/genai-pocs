schemas = {
    "Opportunity": {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "Opportunity": "Launch digital wealth management platform"
    },
    "Challenge": {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "Challenge": "Enhance digital wealth management platform security"
    },
    "ActionItem": {
        "clientID": "GC001",
        "clientName": "Delta Trust Inc.",
        "ActionItem": "Implement a comprehensive security strategy for digital wealth management platform"
    },
    "Revenue": {
        "_id": "6797aa61af157dc5a5f6321f",
        "company": "Sigma Invest Inc.",
        "client_id": "GC002",
        "client_name": "Sigma Invest Inc.",
        "currency": "USD",
        "year": 2015,
        "region": "Global",
        "last_updated": "2024-08-22T15:46:41.529041",
        "equities": 2930080389,
        "derivatives": 1971112342,
        "prime_brokerage": 1863227667
    }
}

# Example usage
#print(schemas["Opportunity"])
#print(schemas["Revenue"])
#print(schemas["Challenge"])

# Output:

def get_schema_keys():
    return list(schemas.keys())

print(get_schema_keys())