# Copyright 2023 Fe-Ti aka T.Kravchenko

import urllib.request as u_request # TODO: make async http

from typing import Union
from pathlib import Path

def make_url(
                scheme : str,
                server_root : Path,
                resource_path,
                parameters : dict | str,
                api_format='.json'
            ):
    """!
    This function assembles a URL from given parameters.
    """
    # Let's check types
    # ~ if type(server_root) is Path:
        # ~ raise TypeError("Server root should be a Path object like 'host/path/to/redmine'")
    if type(parameters) is dict:
        # if parameters are present as dict, then make a string out of them
        parameters_string = ""
        for k in parameters.keys():
            parameters_string += f"{k}={parameters[k]}&"
        parameters_string = parameters_string[:-1]
    elif type(parameters) is str:
        parameters_string = parameters
    else:
        raise TypeError("Parameters should be either in dict or URL parameters string form")
    return f"{scheme}://{server_root / resource_path}{api_format}?{parameters_string}"

# HTTP Requests -- all of them return response string

def  _sync_get_response(req, encoding):
    try:
        with u_request.urlopen(req) as f:
            return {"data":f.read().decode(encoding), "code":f.code}
    except u_request.HTTPError as error:
        with error as f:
            return {"data":f.read().decode(encoding), "code":f.code}
            
# todo: write async http req
# ~ def _async_get_response():
    # ~ pass

def GET(url : str, encoding : str ='utf-8'):
    """!
    GET is used for getting info. Returns string.
    """
    req = u_request.Request(url=url, data=None, method="GET")
    return _sync_get_response(req, encoding)

def DELETE(url : str, encoding : str ='utf-8'):
    """!
    DELETE removes object, which corresponds to given URL, e.g. an issue.
    """
    req = u_request.Request(url=url, data=None, method="DELETE")
    return _sync_get_response(req, encoding)


def POST(url : str, data : str, encoding : str ='utf-8'):
    """!
    POST is used for creating objects.
    """
    req = u_request.Request(url=url,
                            data=bytes(data, encoding),
                            method="POST",
                            headers={"Content-Type": f"application/json"})
    return _sync_get_response(req, encoding)

def PUT(url : str, data : str, encoding : str ='utf-8'):
    """!
    PUT is used for modifying objects, which correspond to given URL.
    """
    req = u_request.Request(url=url,
                            data=bytes(data, encoding),
                            method="PUT",
                            headers={"Content-Type": f"application/json"})
    return _sync_get_response(req, encoding)
