# (Yet another) Redmine Bot Library

# Goals:
# - use Redmine JSON REST API (maybe in future supoort XML)
# - provide a simple bot logic which
# - be able to:
#     - create/delete:
#         - projects
#         - issues
#     - assign issues to user
#     - add watchers to issues
#     - get:
#         - project list
#         - issues:
#             - by number
#             - listed in project (with filtering);
#             - assigned to user
#             - which are watched by user

import json

from http_req_lib import GET, POST, PUT, DELETE, make_url

# "Main" library part
class RedmineObject:
    def attributes_as_dict(self):
        dictionary = self.__dict__{:}
        for key in dictionary.keys():
            if dictionary[key] = None:
                del dictionary[key]
        return dictionary

class Project(RedmineObject):
"""
    project (required): a hash of the project attributes, including:
        name (required): the project name
        identifier (required): the project identifier
        description
        homepage
        is_public: true or false
        parent_id: the parent project number
        inherit_members: true or false
        default_assigned_to_id: ID of the default user. It works only when the new project is a subproject and it inherits the members.
        default_version_id: ID of the default version. It works only with existing shared versions.
        tracker_ids: (repeatable element) the tracker id: 1 for Bug, etc.
        enabled_module_names: (repeatable element) the module name: boards, calendar, documents, files, gantt, issue_tracking, news, repository, time_tracking, wiki.
        issue_custom_field_ids: (repeatable element) issue custom field id.
        custom_field_values: array with id => value pairs
"""
    def __init__(self, name : str,
                    identfier : str,
                    description : str = None,
                    homepage : str = None,
                    is_public : bool = True,
                    parent_id : int = None,
                    inherit_members : bool = False):
        
    def to_dict(self):
        return {"project" : self.attributes_as_dict()}

class Issue(RedmineObject):
"""
    issue - A hash of the issue attributes:
        project_id
        tracker_id
        status_id
        priority_id
        subject
        description
        category_id
        fixed_version_id - ID of the Target Versions (previously called 'Fixed Version' and still referred to as such in the API)
        assigned_to_id - ID of the user to assign the issue to (currently no mechanism to assign by name)
        parent_issue_id - ID of the parent issue
        custom_fields - See Custom fields
        watcher_user_ids - Array of user ids to add as watchers (since 2.3.0)
        is_private - Use true or false to indicate whether the issue is private or not
        estimated_hours - Number of hours estimated for issue
"""
    def __init__(self, subject : str,
                    description : str = None):
        
    def to_dict(self):
        return {"issue" : self.attributes_as_dict()}

class ServerControlUnit:
    
    def __init__(self, server_root : str|Path, use_https : bool = True):
        self.server_root = Path(server_root)
        self.http_scheme = "http"+"s"*use_https # I'm genious, LOL

    # Project-related methods
    def get_project_list(self, parameters : dict|Project):
        if not type(parameters) is dict:
            parameters = parameters.to_dict()
        try:
            return json.loads(GET(make_url(self.http_scheme,
                                                self.server_root,
                                                PROJECTS,
                                                parameters)))
        except Exception as error:
            return str(error)

    def create_project(self, parameters):
        if not type(parameters) is dict:
            parameters = parameters.to_dict()
        try:
            return json.loads(POST(make_url(self.http_scheme,
                                            self.server_root,
                                            PROJECTS,
                                            parameters)))
        except Exception as error:
            return str(error)
    def edit_project(self, parameters):
        if not type(parameters) is dict:
            parameters = parameters.to_dict()
        try:
            return json.loads(PUT(make_url(self.http_scheme,
                                            self.server_root,
                                            PROJECTS,
                                            parameters)))
        except Exception as error:
            return str(error)
    def delete_project(self, parameters):
        return json.loads(GET(make_url(self.http_scheme,
                                                self.server_root,
                                                PROJECTS,
                                                parameters)))

    # Task-related methods
    def get_issue_list(self, parameters):
        try:
            if self.use_https:
                 return json.loads(GET(make_url('https',
                                                self.server_root,
                                                ISSUES,
                                                parameters)))
            else:
                return json.loads(GET(make_url('http',
                                                self.server_root,
                                                ISSUES,
                                                parameters))) 
        except Exception as error:
            return str(error)
    def create_issue(self, parameters):
        pass
    def edit_issue(self, parameters):
        pass
    def delete_issue(self, parameters):
        pass
 

