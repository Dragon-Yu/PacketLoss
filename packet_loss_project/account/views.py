from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from account.forms import UserForm, PasswordForm
from funcs.json_response import *
from funcs.decorators import load_json_data, login_required
from funcs.common_funcs import *
from packet.models import Packet, Comment


@load_json_data(('username', check_username),
                ('password', check_password))
def user_login(request, received_data={}):
    username = received_data['username']
    password = received_data['password']

    user = authenticate(username=username, password=password)
    if user:
        if user.is_active:
            login(request, user)
            return true_json_response(msg="Login success")
        else:
            return false_json_response(msg="Your account is disabled")
    else:
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return false_json_response(msg="No such user")
        else:
            return false_json_response(msg="Password incorrect")


@load_json_data(('username', check_username),
                ('password', check_password))
def register(request, received_data={}):
    # [TODO] response with fail reasons when not success
    user_form = UserForm(data=received_data)
    if user_form.is_valid():
        user = user_form.save(commit=False)
        user.set_password(user.password)
        user.save()
        return true_json_response(msg="Register success")
    else:
        error_dict = json.loads(user_form.errors.as_json())
        print(error_dict)
        return false_json_response(data=error_dict, msg="Register fail")


@login_required
def user_logout(request):
    # [NOTICE] this is not a defined API
    logout(request)
    return true_json_response(msg="Logout success")


@login_required
@load_json_data(('old_password', check_password),
                ('new_password', check_password))
def change_password(request, received_data={}):
    user = authenticate(username=request.user.username, password=received_data['old_password'])
    if user:
        password_form = PasswordForm(data={'password': received_data['new_password']})
        if password_form.is_valid():
            user.set_password(received_data['new_password'])
            user.save()
            login(request, user)
            return true_json_response("Password changed")
        else:
            return false_json_response("Password format not valid")
    else:
        return false_json_response("Old password not correct")            
    
@login_required
def user_details(request):
    data = {}
    data['username'] = request.user.username
    data['credit'] = calculate_credit(request.user)
    packets = Packet.objects.filter(creator=request.user)
    data['total_packets'] = len(packets)
    comments = Comment.objects.filter(user=request.user)
    data['total_comments'] = len(comments)
    data['total_likes'] = 0
    data['total_dislikes'] = 0
    for packet in packets:
        data['total_likes'] += packet.likes
        data['total_dislikes'] += packet.dislikes
    return true_json_response(data=data, msg="Get user details successfully")
