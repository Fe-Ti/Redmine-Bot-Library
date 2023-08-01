
import urllib.request as u_request # TODO: make async http

from typing import Union
from pathlib import Path

ISSUES = Path('issues')
PROJECTS = Path('projects')
USERS = Path('users')



def make_url(scheme, server_root : Path, resource_path, parameters : dict, api_format='.json'):
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

def GET(url, encoding='utf-8'):
    """!
    GET is used for getting info. Returns string.
    """
    req = u_request.Request(url=url, data=None, method="GET")
    with u_request.urlopen(req) as f:
        return(f.read().decode(encoding))

def DELETE(url, encoding='utf-8'):
    """!
    DELETE removes object, which corresponds to given URL, e.g. an issue.
    """
    req = u_request.Request(url=url, data=None, method="DELETE")
    with u_request.urlopen(req) as f:
        return(f.read().decode(encoding))


def POST(url, data : str, encoding='utf-8', api_format='json'):
    """!
    POST is used for creating objects.
    """
    req = u_request.Request(
                            url=url,
                            data=bytes(data, encoding),
                            method="POST",
                            # uncomment below if xml support is implemented
                            # ~ headers={"Content-Type": f"application/{json}"}
                            headers={"Content-Type": f"application/json"}
                            )
    with u_request.urlopen(req) as f:
        return(f.read().decode(encoding))

def PUT(url, data : str, encoding='utf-8'):
    """!
    PUT is used for modifying objects, which correspond to given URL.
    """
    req = u_request.Request(
                            url=url,
                            data=bytes(data, encoding),
                            method="PUT",
                            # uncomment below if xml support is implemented
                            # ~ headers={"Content-Type": f"application/{json}"}
                            headers={"Content-Type": f"application/json"}
                            )
    with u_request.urlopen(req) as f:
        return(f.read().decode(encoding))
