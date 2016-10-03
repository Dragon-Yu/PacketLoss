import json
from django.http import JsonResponse

def formatted_json_response(success="false", data={}, msg=""):
    d = {'success':success,
         'data':data,
         'msg':msg,}
    return JsonResponse(d)

def false_json_response(data={}, msg=""):
    return formatted_json_response(success="false", data=data, msg=msg)

def true_json_response(data={}, msg=""):
    return formatted_json_response(success="true", data=data, msg=msg)
