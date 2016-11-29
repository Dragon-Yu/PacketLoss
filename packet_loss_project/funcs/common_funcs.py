from exceptions import InvalidValue
from decimal import Decimal

def calculate_credit(user):
    # [TODO] impliment this function
    return 100

def check_id(x):
    """
    if can convert x to a int, return int(x)
    else raise an error
    """
    try:
        id = int(x)
        assert(id > 0)
    except:
        raise(InvalidValue("Invalid id"))
    else:
        return id

def check_lng(x):
    """
    check if 180 < longitude <= 180
    """
    try:
        lng = Decimal(x)
        assert(lng > -180)
        assert(lng <= 180)
    except:
        raise(InvalidValue("Invalid longitude"))
    else:
        return lng

def check_lat(x):
    """
    check if -90 <= latitude <= 90
    """
    try:
        print(x)
        lat = Decimal(x)
        print(lat)
        assert(lat >= -90)
        assert(lat <= 90)
    except:
        raise(InvalidValue("Invalid latitude"))
    else:
        return lat

def check_not_empty_string(x, error_message="Invalid string"):
    """
    check if x a string and if it is empty
    """
    try:
        s = unicode(x)
        assert(s)
    except:
        raise(InvalidValue(error_message))
    else:
        return s

def check_username(x):
    return check_not_empty_string(x, error_message="Invalid username")

def check_password(x):
    return check_not_empty_string(x, error_message="Invalid password")

def check_packet_name(x):
    return check_not_empty_string(x, error_message="Packet name cann't be empty")

def check_content(x):
    return check_not_empty_string(x, error_message="Content cann't be empty")

def check_delay(x):
    """
    check if x can convert to int and 0 <= x <= 86400
    """
    try:
        delay = int(x)
        assert(delay >= 0)
        assert(delay <= 86400)
    except:
        raise(InvalidValue('Invalid delay value'))
    else:
        return delay

def check_timeout(x):
    """
    check if x can convert to int
    if x < 0 return 31536000(the seconds of a year)
    else return min(x, 31536000)    
    """
    try:
        timeout = int(x)
        if (timeout < 0):
            timeout = 31536000
        else:
            timeout = min(31536000, timeout)
    except:
        raise(InvalidValue("Invalid timeout"))
    else:
        return timeout

def check_creator_only(x):
    """
    if x == "true" return True
    else return fales
    """
    return (x == 'true')

def check_ratings(x):
    """
    check if x == 1 or x == -1 or x == 0
    """
    try:
        ratings = int(x)
        if ratings != -1 and ratings != 1 and ratings != 0:
            raise(InvalidValue())
    except:
        raise(InvalidValue("Invalid ratings"))
    else:
        return ratings

