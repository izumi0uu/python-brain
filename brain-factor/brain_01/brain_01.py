import requests
import json
from os.path import expanduser
from requests.auth import HTTPBasicAuth


# with open(expanduser('account.txt')) as f:
#     credentials = json.load(f)

# username, password = credentials

username = "zard200107@gmail.com"
password = "229534941k."

try:
    session = requests.Session()

    session.auth = HTTPBasicAuth(username, password)

    response = session.post("https://api.worldquantbrain.com/authentication")
except Exception as e:
    print(e)
    print("Authentication failed")
    exit()

print(response.status_code)
print(response.json())

if response.status_code != 201:
    print("Authentication failed")
    exit()


