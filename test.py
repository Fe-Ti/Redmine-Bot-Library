from main import *

# ~ issue = {
    # ~ "issue": {
        # ~ "project_id": 1,
        # ~ "subject": "Example Пример",
        # ~ "priority_id": 4,
        # ~ "tracker_id": 1,
        # ~ "status_id":1
    # ~ }
# ~ }\

# ~ issue = {
    # ~ "issue": {
        # ~ "project":{"id": 1},
        # ~ "subject": "Example",
        # ~ "priority":{"id": 4}
    # ~ }
# ~ }

# enter your credzzz here :)
# like so
# srvkey = 'APIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIKEYAPIK'
# Example for non-prod local test server
server_root = Path('localhost/redmine')
srvkey = 'c42be51d95aa76c882debf1a58547fe07da32b66'
srvkey = '8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6'

api_fmt = '.json'
params = {"key" : srvkey, "limit" : 100}
scu = ServerControlUnit(server_root, use_https=False)
print(json.dumps(scu.get_project_list(params), indent=4, ensure_ascii=False))
print ("-"*40)
print(json.dumps(scu.get_issue_list(params), indent=4, ensure_ascii=False))
params = {"key" : srvkey, "id" : 1}
print(scu.show_project(params).to_dict())



