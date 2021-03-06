from decimal import Decimal, InvalidOperation
from datetime import timedelta
from math import cos, radians

from django.shortcuts import render
from django.utils import timezone

from funcs.json_response import true_json_response, false_json_response
from funcs.decorators import load_json_data, login_required
from funcs.common_funcs import *
from models import Packet, Comment


def __get_nearby_packets(longitude, latitude, user):
    # set a longitude and latitude offset, then calculate longitude ande latitude bound for a certain point
    # offset 0.01 is approximately equal to 1km

    latitude_offset = Decimal(0.01)
    longitude_offset = Decimal(latitude_offset / Decimal(cos(radians(latitude))))
    packets = Packet.objects.filter(longitude__range=(longitude - longitude_offset, longitude + longitude_offset),
                                    latitude__range=(latitude - latitude_offset, latitude + latitude_offset))
    packets = packets.filter(owner=None)
    packets = packets.exclude(ignorers=user)
    now = timezone.now()
    packets = packets.filter(can_see_time__lt=now)
    packets = packets.filter(die_time__gt=now)
    packets = packets.exclude(last_owner=user)

    return packets

@login_required
@load_json_data(('packet_name', check_packet_name),
                ('content', check_content),
                ('lat', check_lat),
                ('lng', check_lng),
                ('delay', check_delay),
                ('timeout', check_timeout))
def drop(request, received_data={}):
    # delay and timeout's unit is second
    # [TODO] add the restriction: one person can drop 60 packets at most within an hour

    name = received_data['packet_name']
    content = received_data['content']
    longitude = received_data['lng']
    latitude = received_data['lat']
    delay = received_data['delay']
    timeout = received_data['timeout']

    create_time = timezone.now()
    can_see_time = create_time + timedelta(seconds=delay)
    die_time = create_time + timedelta(seconds=timeout)
    user = request.user
    packet = Packet(name=name, content=content, latitude=latitude,
                    longitude=longitude, create_time=create_time, creator=user,
                    can_see_time=can_see_time, die_time=die_time, last_owner=user)
    packet.save()
    packet.owneders.add(user)
    return true_json_response(msg="Packet dropped")


@login_required
@load_json_data(('lat', check_lat),
                ('lng', check_lng))
def get_nearby_packets(request, received_data={}):
    # [TODO] refactor this piece of ugly code
    longitude = received_data['lng']
    latitude = received_data['lat']

    packets = __get_nearby_packets(longitude, latitude, request.user)

    response_data = []
    for packet in packets:
        response_data.append({'id': packet.id,
                              'lng': float(packet.longitude),
                              'lat': float(packet.latitude),})

    return true_json_response(data=response_data, msg="Get nearby packets success")


@login_required
@load_json_data(('id', check_id),
                ('lng', check_lng),
                ('lat', check_lat))
def pick(request, received_data={}):
    id = received_data['id']
    longitude = received_data['lng']
    latitude = received_data['lat']

    nearby_packets = __get_nearby_packets(longitude, latitude, request.user)
    try:
        packet = nearby_packets.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response(msg="Invalid operation")
    # [TODO] add can_see_time and 

    packet.owneders.add(request.user)
    packet.owner = request.user
    packet.last_owner = request.user
    packet.save()

    response_data = {'packet_name': packet.name,
                     'content': packet.content,}
    return true_json_response(data=response_data, msg="Pick up success")


@login_required
@load_json_data(('id', check_id),
                ('comment', None),
                ('creator_only', check_creator_only),
                ('ratings', check_ratings))
def redrop(request, received_data):
    id = received_data['id']
    comment = received_data['comment']
    only_creator_can_see = received_data['creator_only']
    ratings = received_data['ratings']

    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response(msg="Packet does not exist")

    user = request.user
    if packet.owner != user:
        return false_json_response(msg="Premission denied, this packet not belongs to you")

    # [TODO] test this piece of code
    if len(comment) != 0:
        comment = Comment(packet=packet, user=user, content=comment, only_creator_can_see=only_creator_can_see)
        comment.save()
    packet.owner = None
    if ratings == 1:
        packet.likes += 1
    elif ratings == -1:
        packet.dislikes += 1
    packet.save()

    return true_json_response(msg="Redrop success")


@login_required
@load_json_data(('page_id', check_id))
def get_owning_packets(request, received_data):
    # [TODO] page_id now is useless in this version, the function will return all owning packets
    page_id = received_data['page_id']

    packets = Packet.objects.filter(owner=request.user).order_by('-create_time')

    data = []
    for packet in packets:
        data.append({'id': packet.id,
                     'packet_name': packet.name,
                     'username': packet.creator.username,
                     'credit': calculate_credit(packet.creator),
                     'create_time': packet.create_time.strftime("%Y-%m-%d"),
                     'likes': packet.likes,
                     'dislikes': packet.dislikes,})

    return true_json_response(data=data, msg="Get owning packets success")


@login_required
@load_json_data(('page_id', check_id))
def get_owned_packets(request, received_data):
    page_id = received_data['page_id']

    packets = request.user.owned_packets.exclude(ignorers=request.user).order_by(
        '-create_time')

    # [TODO] refactor duplicated code (in get owning packets)
    data = []
    for packet in packets:
        data.append({'id': packet.id,
                     'packet_name': packet.name,
                     'username': packet.creator.username,
                     'credit': calculate_credit(packet.creator),
                     'create_time': packet.create_time.strftime("%Y-%m-%d"),
                     'likes': packet.likes,
                     'dislikes': packet.dislikes,})
    return true_json_response(data=data, msg="Get owned packets success")


@login_required
@load_json_data(('id', check_id))
def get_packet_details(request, received_data):
    id = int(received_data['id'])

    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoewNotExist:
        return false_json_response(msg="Packet does not exist")

    try:
        packet.owneders.get(username=request.user.username)
    except User.DoesNotExist:
        return false_json_response(msg="Permission denied, you don't have right to open get this packet's details")

    data = {'id': packet.id,
            'packet_name': packet.name,
            'username': packet.creator.username,
            'credit': calculate_credit(packet.creator),
            'create_time': packet.create_time.strftime("%Y-%m-%d"),
            'likes': packet.likes,
            'dislikes': packet.dislikes,
            'comments': [],
            'content': packet.content,}
    comments = Comment.objects.filter(packet=packet)

    for comment in comments:
        if comment.only_creator_can_see == True:
            if request.user != comment.user or request.user != packet.user:
                continue
        comment_data = {'content': comment.content,
                        'username': comment.user.username,
                        'create_time': comment.time.strftime("%Y-%m-%d"),}
        data['comments'].append(comment_data)

    return true_json_response(data=data, msg="Get packet details success")


@login_required
@load_json_data(('id', check_id))
def ignore(request, received_data):
    id = int(received_data['id'])
    # [TODO] dismiss code duplication
    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response(msg="Packet does not exist")

    try:
        packet.owneders.get(username=request.user.username)
    except User.DoesNotExist:
        return false_json_response(msg="Permission denied, you don't have right to ignore the packet")

    if packet.owner == request.user:
        packet.owner = None
        packet.save()

    packet.ignorers.add(request.user)

    return true_json_response(msg="Ignore success")
