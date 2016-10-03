import json
from json_response import *

JSON_FORMAT_ERROR_MSG = "Invalid json format"

def _get_received_data(request, *args):
    """
    check request format and return a dict from json data.
    1. check it's content type is "applicaton/json"
    2. check every field in args is in the json data
    """ 
    if (request.META.get('CONTENT_TYPE') != "application/json"):
        return None

    try:
        received_data = json.loads(request.body)
        for key in args:
            received_data[key]
    except:
        return None
    else:
        return received_data
    

def load_json_data(*args):
    def decorator(func):
        def wrapper(request):
            received_data = _get_received_data(request, *args)
            if (not received_data):
                return false_json_response(msg=JSON_FORMAT_ERROR_MSG)
            return func(request, received_data)

        return wrapper

    return decorator

def login_required(func):
    def wrapper(request):
        if not request.user.is_authenticated():
            return false_json_response(msg="Please login first")
        return func(request)
    return wrapper
