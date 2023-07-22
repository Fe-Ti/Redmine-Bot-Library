from main import *

issue = {
    "issue": {
        "project_id": 1,
        "subject": "Example Пример",
        "priority_id": 4,
        "tracker_id": 1,
        "status_id":1
    }
}

# ~ issue = {
    # ~ "issue": {
        # ~ "project":{"id": 1},
        # ~ "subject": "Example",
        # ~ "priority":{"id": 4}
    # ~ }
# ~ }

# enter your credzzz here :)
# like so
# scheme = "https"
# srvkey = 'APIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIK'
# Example for non-prod local test server
server_root = Path('localhost/redmine')
scheme = "http"
srvkey = 'c42be51d95aa76c882debf1a58547fe07da32b66'
srvkey = '8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6'

api_fmt = '.json'

url = make_url(scheme, server_root, ISSUES, f"key={srvkey}")
print(url)
print(json.loads(GET(url)))

url = make_url(scheme, server_root, ISSUES, f"key={srvkey}")
print(url)
print(json.dumps(issue))
print(json.loads(POST(url, json.dumps(issue))))

url = make_url(scheme, server_root, ISSUES, f"key={srvkey}")
print(url)
print(json.loads(GET(url)))
