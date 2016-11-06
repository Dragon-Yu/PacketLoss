from decimal import Decimal, InvalidOperation

from django.shortcuts import render

from funcs.json_response import true_json_response, false_json_response
from funcs.decorators import load_json_data, login_required
from models import Packet, Comment

from math import cos, radians

def __get_nearby_packets(longitude, latitude, user):
    # set a longitude and latitude offset, then calculate longitude ande latitude bound for a certain point                

    # offset 0.01 is approximately equal to 1km                                                                            

    latitude_offset = Decimal(0.01)
    longitude_offset = Decimal(latitude_offset / Decimal(cos(radians(latitude))))
    packets = Packet.objects.filter(longitude__range=(longitude - longitude_offset, longitude + longitude_offset),latitude__range=(latitude - latitude_offset, latitude + latitude_offset)).exclude(owner=user)
    return packets


@login_required
@load_json_data('packet_name', 'content', 'lat', 'lng')
def drop(request, received_data={}):
    name = received_data['packet_name']
    content = received_data['content']

    # [TODO] refactor this piece of ugly code
    try:
        longitude = Decimal(received_data['lng'])
        latitude = Decimal(received_data['lat'])
    except InvalidOperation:
        return false_json_response(mst="Invalid longitude or latitude")

    if (longitude <= -180 or longitude > 180 or latitude < -90 or latitude > 90):
        return false_json_response(msg="Invalid longitude or latitude")

    if len(content) == 0:
        return false_json_response(msg="Content cannot be empty")
        
    user = request.user
    packet = Packet(name=name, content=content, latitude = latitude,
                    longitude=longitude, creator=user)
    packet.save()
    packet.owneders.add(user)
    return true_json_response(msg="Packet dropped")

@login_required
@load_json_data('lat', 'lng')
def get_nearby_packets(request, received_data={}):
    # [TODO] refactor this piece of ugly code
    try:
        longitude = Decimal(received_data['lng'])
        latitude = Decimal(received_data['lat'])
    except InvalidOperation:
        return false_json_response(msg="Invalid longitude or latitude")

    if (longitude <= -180 or longitude > 180 or latitude < -90 or latitude > 90):
        return false_json_response(msg="Invalid longitude or latitude")

    packets = __get_nearby_packets(longitude, latitude, request.user)

    response_data = []
    for packet in packets:
        response_data.append({'id': packet.id,
                         'lng': float(packet.longitude),
                         'lat': float(packet.latitude),})
    
    return true_json_response(data=response_data, msg="Get nearby packets success")

@login_required
@load_json_data('id', 'lng', 'lat')
def pick(request, received_data={}):
    # [TODO] refactor this piece of ugly code
    try:
        id = int(received_data['id']) #[NOT SURE] int or other type
    except:
        return false_json_response("Invalid id")
    
    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response("Packet does not exist")

    if (packet.owner != None):
        return false_json_response("Packet already has a owner")
    
    # [TODO] add lng and lat constraint
    
    packet.owneders.add(request.user)
    packet.owner = request.user
    packet.save()
    
    response_data = {'packet_name': packet.name,
                     'content': packet.content,} #[NOT SURE] contents with all comments or just the content
    return true_json_response(data=response_data, msg="Pick up success")

@login_required
@load_json_data('id', 'comment')
def redrop(request, received_data):

    comment = received_data['comment']

    # [TODO] refactor this piece of ugly code
    try:
        id = int(received_data['id']) # [NOT SURE] int or other type
    except:
        return false_json_response("Inavlid id")

    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response("Packet does not exist")

    user = request.user
    if packet.owner != user:
        return false_json_response("Premission denied, this packet not belongs to you")
    
    # [TODO] test this piece of code
    if len(comment) != 0:
        comment = Comment(packet=packet, user=user, content=comment)
        comment.save()
    packet.owner = None
    packet.save()

    return true_json_response("Redrop success")

@login_required
@load_json_data('page_id')
def get_owning_packets(request, received_data):
    # [TODO] refactor
    try:
        page_id = int(received_data['page_id'])
    except:
        return false_json_response("Invalid page_id")

    packets = Packet.objects.filter(owner=request.user).order_by('-create_time')
    
    data = []
    for packet in packets:
        data.append({'id': packet.id,
                     'packet_name': packet.name,
                     'username': packet.creator.username,
                     'create_time': packet.create_time.strftime("%Y-%m-%d"),})

    return true_json_response(data=data, msg="Get owning packets success")

@login_required
@load_json_data('page_id')
def get_owned_packets(request, received_data):
    # [TODO] refactor
    try:
        page_id = int(received_data['page_id'])
    except:
        return false_json_response("Invalid page_id")

    # [NOT SURE!!] don't know the effect
    packets = request.user.owned_packets.exclude(ignorers=request.user).exclude(owner=request.user).order_by('-create_time')

    # [TODO] refactor dumplicated code (in get owning packets)
    data = []
    for packet in packets:
        data.append({'id': packet.id,
                     'packet_name': packet.name,
                     'username': packet.creator.username,
                     'create_time': packet.create_time.strftime("%Y-%m-%d"),})
    return true_json_response(data=data, msg="Get owned packets success")

@login_required
@load_json_data('id')
def get_packet_details(request, received_data):
    # [TODO] refactor this piece of ugly code
    try:
        id = int(received_data['id'])
    except:
        return false_json_response("Invalid id")

    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoewNotExist:
        return false_json_response("Packet does not exist")

    try:
        packet.owneders.get(username=request.user.username)
    except User.DoesNotExist:
        return false_json_response("Permission denied, you don't have right to open get this packet's details")

    data = {'id': packet.id,
            'packet_name': packet.name,
            'username': packet.creator.username,
            'create_time': packet.create_time.strftime("%Y-%m-%d"),
            'comments': [],
            'content': packet.content,}
    comments = Comment.objects.filter(packet=packet)
    
    for comment in comments:
        comment_data = {'content': comment.content,
                        'username': comment.user.username,
                        'create_time': comment.time.strftime("%Y-%m-%d"),}
        data['comments'].append(comment_data)

    return true_json_response(data=data, msg="Get packet details success")

@login_required
@load_json_data('id')
def ignore(request, received_data):
    # [TODO] refactor
    try:
        id = int(received_data['id'])
    except:
        return false_json_response(msg="Invalid id")
    # [TODO] dismiss code dumplicate
    try:
        packet = Packet.objects.get(id=id)
    except Packet.DoesNotExist:
        return false_json_response(msg="Packet does not exist")

    try:
        packet.owneders.get(username=request.user.username)
    except User.DoesNotExist:
        return false_json_response("Permission denied, you don't have right to open get this packet's details")
    
    if packet.owner == request.user:
        packet.owner = None
        packet.save()

    packet.ignorers.add(request.user)

    return true_json_response(msg="Ignore success")

