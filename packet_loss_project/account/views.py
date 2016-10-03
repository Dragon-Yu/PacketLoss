from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from account.forms import UserForm
from funcs.json_response import *
from funcs.decorators import load_json_data, login_required

@load_json_data('username', 'password')
def user_login(request, received_data={}):
    # [DONE] use decorator to replace this kind of duplicated code
    username = received_data.get('username')
    password = received_data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            return true_json_response(msg= "Login success")
        else:
            return false_json_response(msg="Your account is disabled")
    else:
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return false_json_response(msg="No such user")
        else:
            return false_json_response(msg="Password incorrect")
    

@load_json_data('username', 'password')
def register(request, received_data={}):
    # [DONE] validate the username and password format
    user_form = UserForm(data=received_data)
    if user_form.is_valid():
        user = user_form.save(commit=False)
        user.set_password(user.password)
        user.save()
        return true_json_response(msg="Register success")
    else:
        error_dict = json.loads(user_form.errors.as_json())
        return false_json_response(data=error_dict, msg="Register fail")

@login_required
def user_logout(request):
    # [NOTICE] this is not a defined API
    logout(request)
    return true_json_response(msg="Logout success")     
