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
from typing import Union, Any
from pathlib import Path

from http_req_lib import GET, POST, PUT, DELETE, make_url


ISSUES = Path('issues')
PROJECTS = Path('projects')
USERS = Path('users')

ALL_PROJECT_ATTRIBUTE_NAMES = [ "name",
                                "identfier",
                                "description",
                                "homepage",
                                "is_public",
                                "parent_id",
                                "inherit_members",
                                "tracker_ids" ,
                                "enabled_module_names",
                                "issue_custom_field_ids",
                                "custom_field_values",
                                "status",
                                "id" ]
ALL_ISSUE_ATTRIBUTE_NAMES = [
                                "subject"
                                "project_id"
                                "tracker_id"
                                "status_id"
                                "priority_id"
                                "category_id"
                                "description"
                                "fixed_version_id"
                                "assigned_to_id"
                                "parent_issue_id"
                                "custom_fields"
                                "watcher_user_ids"
                                "is_private"
                                "estimated_hours"
                                "id" ]
# "Main" library part
class RedmineObject:
    _available_attr_names = list()
    def __attributes_as_dict(self, only_changed_attrs = True):
        """
        
        """
        dictionary = dict()
        if only_changed_attrs:
            keys = self._changed_attributes
        else:
            keys = self.__dict__.keys()
        for key in keys:
            if not ( (self.__dict__[key] == None) or (key.startswith("_")) ):
                dictionary[key] = self.__dict__[key]
        return dictionary

    def update_attribute(self, attr_name, attr_value):
        if attr_name not in self._available_attr_names:
            raise AttributeError(f"Wrong attribute name {attr_name}. Should be one of {self._available_attr_names}")
        self._changed_attributes.append(attr_name)
        setattr(self, attr_name, attr_value)
        

    def update_with_dict(self, dictionary : dict):
        for key, val in dictionary:
            update_attribute(key, val)

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

    Additional field:
    int_id - integer identifier ('cause projects actually have such a thing)
"""
class Project(RedmineObject):
    _available_attr_names = ALL_PROJECT_ATTRIBUTE_NAMES
    def __init__(self,
                    name : str,
                    identifier : str,
                    description : str = None,
                    homepage : str = None,
                    status : int = None,
                    is_public : bool = True,
                    parent_id : int = None,
                    inherit_members : bool = False,
                    tracker_ids : list[int] = None,
                    enabled_module_names : list[str] = None,
                    issue_custom_field_ids : list[int] = None,
                    custom_fields : list[dict[str, Any]] = None,
                    id : int = None # we don't know this thing on creation
                ):
        self.name : str = name
        self.identfier : str = identfier
        self.description : str = description
        self.homepage : str = homepage
        self.is_public : bool = is_public
        self.parent_id : int = parent_id
        self.inherit_members : bool = inherit_members
        self.tracker_ids : list[int] = tracker_ids[:]
        self.enabled_module_names : list[str] = enabled_module_names[:]
        self.issue_custom_field_ids : list[int] = issue_custom_field_ids[:]
        self.custom_field_values : dict[int, str] = custom_field_values.copy()
        self.id : int = id
        if not self.id:
            self._changed_attributes = set(self._available_attr_names)

    def to_dict(self, for_updating = False):
        return {"project" : self.__attributes_as_dict(for_updating)}


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

class Issue(RedmineObject):
    _available_attr_names = ALL_ISSUE_ATTRIBUTE_NAMES
    def __init__(self,
                    subject : str, #Mandatory
                    project_id : int, #Mandatory
                    tracker_id : int, #Mandatory
                    status_id : int, #Mandatory
                    priority_id : int, #Mandatory
                    category_id : int = None,
                    description : str = None,
                    fixed_version_id : int = None,
                    assigned_to_id : int = None,
                    parent_issue_id : int = None,
                    custom_fields : list[dict[str, Any]] = None,
                    watcher_user_ids : list[int] = None,
                    is_private : bool = None,
                    estimated_hours : int = None,
                    id : int = None
                ):
        self.subject : str = subject
        self.project_id : int = project_id
        self.tracker_id : int = tracker_id
        self.status_id : int = status_id
        self.priority_id : int = priority_id
        self.category_id : int = category_id
        self.description = description
        self.fixed_version_id : int = fixed_version_id
        self.assigned_to_id : int = assigned_to_id
        self.parent_issue_id : int = parent_issue_id
        self.custom_fields : list[dict[str, Any]] = custom_fields
        self.watcher_user_ids : list[int] = watcher_user_ids
        self.is_private : bool = is_private
        self.estimated_hours : int = estimated_hours
        self.id : int = id
        if not self.id:
            self._changed_attributes = set(self._available_attr_names)

    def to_dict(self):
        return {"issue" : self.attributes_as_dict()}


class ServerControlUnit:

    def __init__(self, server_root : str|Path, use_https : bool = True):
        self.server_root = Path(server_root)
        self.http_scheme = "http"+"s"*use_https # I'm genious, LOL


    def _mix_parameters(self, parameters, user_key):
        """!
        <Internal function>

        Function for mixing user key with parameters (also converting them to dictionary).
        """
        if not (type(parameters) is dict):
            parameters = parameters.to_dict()
        if user_key:
            parameters["key"] = user_key
        return parameters

    def _get_object_list(self, api_resource : str, parameters : dict, user_key : str):
        parameters = self._mix_parameters(parameters, user_key)
        return json.loads(GET(make_url(self.http_scheme,
                                            self.server_root,
                                            api_resource,
                                            parameters)))

    def _show_object(self, api_resource : str, parameters, user_key : str):
        parameters = self._mix_parameters(parameters, user_key)
        return json.loads(GET(make_url(self.http_scheme,
                                            self.server_root,
                                            api_resource / str(parameters["id"]),
                                            parameters)))

    def _create_object(self, api_resource : str, parameters, user_key : str):
        parameters = mix_parameters(parameters, user_key)
        return json.loads(POST(make_url(self.http_scheme,
                                        self.server_root,
                                        api_resource,
                                        parameters)))

    def _update_object(self, api_resource : str, parameters, user_key : str):
        parameters = mix_parameters(parameters, user_key)
        return json.loads(PUT(make_url(self.http_scheme,
                                        self.server_root,
                                        api_resource / str(parameters["id"]),
                                        parameters)))

    def _delete_object(self, api_resource : str, object_id : int, user_key : str):
        parameters = {"key" : user_key}
        return json.loads(DELETE(make_url(self.http_scheme,
                                                self.server_root,
                                                api_resource / str(object_id),
                                                parameters)))

    # Project-related methods
    def get_project_list(self, parameters : dict, user_key : str = None):
        return self._get_object_list(PROJECTS, parameters, user_key)

    def show_project(self, parameters : Project | dict, user_key : str = None):
        return Project(**self._show_object(PROJECTS, parameters, user_key)["project"])

    def create_project(self, parameters : Project, user_key : str = None):
        return self._create_object(PROJECTS, parameters, user_key)

    def update_project(self, parameters : Project | dict, user_key : str = None):
        return self._update_object(PROJECTS, parameters, user_key)

    def delete_project(self, project_id : int, user_key : str = None):
        return self._delete_object(PROJECTS, project_id, user_key)

    # Task-related methods
    def get_issue_list(self, parameters : dict, user_key : str = None):
        return self._get_object_list(ISSUES, parameters, user_key)

    def show_issue(self, parameters : Issue | dict, user_key : str = None):
        return self._show_object(ISSUES, parameters, user_key)

    def create_issue(self, parameters : Issue, user_key : str = None):
        return self._create_object(ISSUES, parameters, user_key)

    def update_issue(self, parameters : Issue | dict, user_key : str = None):
        return self._update_object(ISSUES, parameters, user_key)

    def delete_issue(self, issue_id : int, user_key : str = None):
        return self._delete_object(ISSUES, issue_id, user_key)


