import requests
import json
from bis_api import COMMON_PAYLOAD, HEADERS, REVIEW_SERVICE

payload = {
    "encDepartmentId": "eyJpdiI6Ilk3RlNkMnJXc0hFMTQ4bDlUaURqdHc9PSIsInZhbHVlIjoiV0RVbUdQYUlnemRyd09ZSTNNOE1JZz09IiwibWFjIjoiOWM2MmI1NDc3NzIwZTFmNjdiMWVjZmEwZWY0ZjZjZGM5MDA5YmQ3Yzg0MTRjOTc3MDBmOTg3NmVlNGZkYTczMCIsInRhZyI6IiJ9",
    "typeSelected": 7,
    "offset": 0,
    "limit": 12,
    "ministryIds": [],
    "sdgIds": [],
    "techCommitteeId": 0,
    **COMMON_PAYLOAD,
}

print("Payload being sent:")
print(json.dumps(payload))

url = f"{REVIEW_SERVICE}/getWebsitePSTechDepartmentWise"
resp = requests.post(url, json=payload, headers=HEADERS)
print(f"Status: {resp.status_code}")
print("Response:")
print(json.dumps(resp.json(), indent=2))
