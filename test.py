from main import *


# ~ issue_creator = {
    # ~ "issue": {
        # ~ "project_id": 1,
        # ~ "subject": "Example",
        # ~ "priority_id": 4
    # ~ }
# ~ }

# ~ getter_string = json.dumps(getter)

# Non prod key for local test server
scheme = "http"
srvkey = 'c42be51d95aa76c882debf1a58547fe07da32b66'

# enter your credzzz here :)
# ~ scheme = "https"
# ~ srvkey = 'APIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIK'
server_root = Path('localhost/redmine')




api_fmt = '.json'

url = make_url(scheme, server_root, ISSUES, f"key={srvkey}")
print(url)
print(json.loads(GET(url)))
