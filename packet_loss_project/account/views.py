import json

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def _get_received_data(request, *args):
    """
    check request format and return a dict from json data.
    1. check it's content type is "applicaton/json"
    2. check every field in args is in the json data
    """ 
    if (request.META.get('CONTENT_TYPE') != "applicaton/json"):
        return None

    try:
        received_data = json.loads(request.body)
        for key in args:
            received_data[key]
    except:
        return None
    else:
        return received_data

def _formatted_json_response(success="false", data={}, msg=""):
    d = {'success':success,
         'data':data,
         'msg':msg,}
    return JsonResponse(d)

def _false_json_response(msg=""):
    return _formatted_json_response(success="false", data={}, msg=msg)

def _true_json_response(data={}, msg=""):
    return _formatted_json_response(success="true", data=data, msg=msg)

def user_login(request):
    received_data = _get_received_data(request, 'username', 'password')
    if (not received_data):
        return _false_json_response(msg="Invalid json format")
    username = received_data.get('username')
    password = received_data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            return _true_json_response(msg= "Login success")
        else:
            return _false_json_response(msg="Your account is disabled")
    else:
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return _false_json_response(msg="No such user")
        else:
            return _false_json_response(msg="Password incorrect")
    


def register(request):
    pass
    
