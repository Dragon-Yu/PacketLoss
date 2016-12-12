import json
from json_response import *
from common_funcs import *
from exceptions import InvalidValue

JSON_FORMAT_ERROR_MSG = "Invalid json format"


def _get_received_data(request, *args):
    """
    check request format and return a dict from json data.
    check every field in args is in the json data and is the correct type.
    args is of format (fieldname, check_function), the check_function is used to check its value correct or not
    """
    
    received_data = json.loads(request.body)
    for each in args:
        field_name = each[0]
        check_function = each[1]
        if check_function:
            received_data[field_name] = check_function(received_data[field_name])
    return received_data

def load_json_data(*args):
    def decorator(func):
        def wrapper(request):
            try:
                received_data = _get_received_data(request, *args)
            except InvalidValue, e:
                return false_json_response(msg=e.message)
            except Exception, e:
                return false_json_response(msg=JSON_FORMAT_ERROR_MSG)
            else:
                return func(request, received_data)

        return wrapper

    return decorator


def login_required(func):
    def wrapper(request):
        if not request.user.is_authenticated():
            return false_json_response(msg="Please login first")
        return func(request)

    return wrapper
