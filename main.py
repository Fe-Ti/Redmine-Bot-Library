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
import logging
from typing import Union, Any
from pathlib import Path

from http_req_lib import GET, POST, PUT, DELETE, make_url
from http_req_lib import u_request


ISSUES = Path('issues')
PROJECTS = Path('projects')
USERS = Path('users')

def _check_type(variable, acceptable_types):
    if not (type(variable) in acceptable_types):
        raise TypeError(f"Expected {acceptable_types}, not {type(variable)}")

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

    def _load_response(self, resp, expected_code):
        if resp["code"] == expected_code:
            if not resp["data"]:
                return {"data" : None,
                        "success" : True }
            else:
                return {"data" : json.loads(resp["data"]),
                        "success" : True }
        else:
            logging.error(f"Expected code {expected_code}, but recieved {resp['code']}")
            return {"data" : resp["data"],
                    "success" : False }

    def _get_object_list(self,
                            api_resource : str|Path,
                            parameters : dict,
                            user_key : str,
                            expected_code : int = 200):
        _check_type(parameters, [dict])
        parameters = self._mix_parameters(parameters, user_key)
        resp = GET(make_url(self.http_scheme,
                                self.server_root,
                                api_resource,
                                parameters))
        return self._load_response(resp, expected_code)
        

    def _show_object(self,
                        api_resource : str|Path,
                        parameters : dict,
                        user_key : str,
                        expected_code : int = 200):
        _check_type(parameters, [dict])
        parameters = self._mix_parameters(parameters, user_key)
        resp = GET(make_url(self.http_scheme,
                                self.server_root,
                                api_resource / str(parameters["id"]),
                                parameters))
        return self._load_response(resp, expected_code)

    def _create_object(self,
                        api_resource : str|Path,
                        parameters : dict,
                        data : dict,
                        user_key : str,
                        expected_code : int = 201):
        _check_type(parameters, [dict])
        parameters = self._mix_parameters(parameters, user_key)
        resp = POST(make_url(self.http_scheme,
                                self.server_root,
                                api_resource,
                                parameters),
                                json.dumps(data))
        return self._load_response(resp, expected_code)

    def _update_object(self,
                        api_resource : str|Path,
                        parameters : dict,
                        data : dict,
                        user_key : str,
                        expected_code : int = 202):
        _check_type(parameters, [dict])
        parameters = self._mix_parameters(parameters, user_key)
        resp = PUT(make_url(self.http_scheme,
                                self.server_root,
                                api_resource / str(parameters["id"]),
                                parameters),
                                json.dumps(data))
        return self._load_response(resp, expected_code)

    def _delete_object(self,
                        api_resource : str|Path,
                        object_id : int|str,
                        user_key : str,
                        expected_code : int = 204):
        _check_type(object_id, [int, str])
        parameters = {"key" : user_key}
        resp = DELETE(make_url(self.http_scheme,
                                self.server_root,
                                api_resource / str(object_id),
                                parameters))
        return self._load_response(resp, expected_code)

    # Project-related methods
    def get_project_list(self, parameters : dict, user_key : str = None) -> dict:
        http_resp = self._get_object_list(PROJECTS, parameters, user_key)
        return http_resp 
        # ~ return project_list_

    def show_project(self, parameters : dict, user_key : str = None) -> dict:
        return self._show_object(PROJECTS, parameters, user_key)

    def create_project(self, parameters : dict, data : dict, user_key : str = None):
        return self._create_object(PROJECTS, parameters, {"project" : data}, user_key)

    def update_project(self, parameters : dict, data : dict, user_key : str = None):
        return self._update_object(PROJECTS, parameters, {"project" : data}, user_key)

    def delete_project(self, project_id : int|str, user_key : str = None):
        return self._delete_object(PROJECTS, project_id, user_key)

    # Task-related methods
    def get_issue_list(self, parameters : dict, user_key : str = None):
        return self._get_object_list(ISSUES, parameters, user_key)

    def show_issue(self, parameters : dict, user_key : str = None):
        return self._show_object(ISSUES, parameters, user_key)

    def create_issue(self, parameters : dict, data : dict, user_key : str = None):
        return self._create_object(ISSUES, parameters, {"issue" : data}, user_key,data)

    def update_issue(self, parameters : dict, data : dict, user_key : str = None):
        return self._update_object(ISSUES, parameters, {"issue" : data}, user_key)

    def delete_issue(self, issue_id : int, user_key : str = None):
        return self._delete_object(ISSUES, issue_id, user_key)

    def add_watcher(self,
                        issue_id : int,
                        new_watcher_uid : int,
                        user_key : str = None):
        self._create_object(ISSUES / issue_id / "watchers",
                            {"user_id" : new_watcher_uid},
                            user_key)

    def del_watcher(self,
                        issue_id : int,
                        watcher_uid : int,
                        user_key : str = None):
        self._delete_object(ISSUES / issue_id / "watchers" / watcher_uid,
                            user_key)
