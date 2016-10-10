from decimal import Decimal, InvalidOperation

from django.shortcuts import render

from funcs.json_response import true_json_response, false_json_response
from funcs.decorators import load_json_data, login_required
from models import Packet, Comment

from math import cos, radians

def get_nearby_packets(longitude, latitude):
    # set a longitude and latitude offset, then calculate longitude ande latitude bound for a certain point

    # offset 0.01 is approximately equal to 1km
    latitude_offset = 0.01
    longitude_offset = latitude_offset / cos(radians(latitude))
    try:
        packet = Packet.objects.filter(owner__isnull=True)[0:1]
        packet = Packet.objects.filter(longitude__range=(longitude - longitude_offset, longitude + longitude_offset),
                                       latitude__range=(latitude - latitude_offset, latitude + latitude_offset))
    except:
        packet = []
    return packet


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
        
    user = request.user
    packet = Packet(name=name, content=content, latitude = latitude,
                    longitude=longitude, creator=user)
    packet.save()
    packet.owneders.add(user)
    return true_json_response(msg="Packet drooped")

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

    packets = get_nearby_packets(longitude, latitude)    

    response_data = []
    for packet in packets:
        response_data.append({'id': packet.id,
                         'lng': packet.longitude,
                         'lat': packet.latitude,})
    
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

    comment = Comment(packet=packet, user=user, content=comment)
    comment.save()
    packet.owner = None
    packet.save()

    return true_json_response("Redrop success")

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
            'create_time': packet.create_time,
            'comments': [],}
    comments = Comment.objects.filter(packet=packet)
    
    for comment in comments:
        comment_data = {'content': comment.content,
                        'username': comment.user.username,
                        'create_time': comment.time,}
        data['comments'].append(comment_data)

    return true_json_response(data=data, msg="Get packet details success")
