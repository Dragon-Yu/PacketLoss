# created by Dillion
# 2016-11-07
# populate initial data for the project
# the process is below:
# 0. empty the database (db.sqlite3)
# 1. python manage.py makemigerations
# 2. python manage.py migrate
# 3. python funcs/populate.py

import requests
import json
import subprocess
import time

HOST = "http://127.0.0.1:8000"
REGISTER_URL = '/user/register/'
LOGIN_URL = '/user/login/'
DROP_PACKET_URL = '/packet/drop/'
PICK_PACKET_URL = '/packet/pick/'
REDROP_PACKET_URL = '/packet/redrop/'

session = requests.Session()

def post(url, data):
    """
    convert data(dict) to json format, and post it to HOST+url
    """
    data = json.dumps(data)
    response = session.post(HOST + url, data)
    response_data = response.json()
    if (response_data['success'] != 'true'):
        error_message = "Not Success When Post " + data + "To " + HOST + url + ". Response message is '" + response_data['msg'] + "'"
        raise Exception(error_message)
    else:
        return response_data

def new_user(username, password):
    post(REGISTER_URL, {'username': username, 'password': password})

def login(username, password):
    post(LOGIN_URL, {'username': username, 'password': password})

def drop_packet(packet_name, content, lng, lat, delay=0, timeout=60*60*24*365):
    post(DROP_PACKET_URL, {'packet_name': packet_name,
                           'content': content,
                           'lng': lng,
                           'lat': lat,
                           'delay': delay,
                           'timeout': timeout,})

def pick_packet(packet_id, lng, lat):
    post(PICK_PACKET_URL, {'id': packet_id,
                           'lng': lng,
                           'lat': lat,})

def redrop_packet(packet_id, comment):
    post(REDROP_PACKET_URL, {'id': packet_id,
                             'comment': comment,
                             'creator_only': 'false',
                             'ratings': 1,})

def recreate_database():
    print("Recreating database")
    try:
        subprocess.call(["rm", "db.sqlite3"])
        print("remove db.sqlite3 successfully")
    except:
        pass
    subprocess.call(["python", "manage.py", "makemigrations"])
    subprocess.call(["python", "manage.py", "migrate"])
    print("Database recreated")

def populate_data():
    print("Populating data")
    new_user("test_user_1", "123")
    new_user("test_user_2", "123")
    login("test_user_1", "123")
    drop_packet(packet_name="test_packet_name_1", content="test_content_1", lng=121.597093, lat=31.191754)
    drop_packet(packet_name="test_packet_name_2", content="test_content_2", lng=121.607011, lat=31.200199)
    drop_packet(packet_name="test_packet_name_3", content="test_content_3", lng=121.632122, lat=31.210200)
    login("test_user_2", "123")
    pick_packet(packet_id=1, lng=121.597093, lat=31.191754)
    redrop_packet(packet_id=1, comment="test_comment_1") 

    subprocess.call(["python", "manage.py", "createsuperuser"])
    print("Data populated")

if __name__ == "__main__":
    confirm = raw_input("Warnning: This action will recreate your database, are you sure?(y/n)")
    if confirm == 'y':
        recreate_database()
        populate_data()
    else:
        print("No changes made, exiting")
        exit()
