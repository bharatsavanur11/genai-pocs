import json

json_data = json.loads('{"year": 2023, "equities": { "$gt" : 2000000 }}')

print(json_data)