import json
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from packet.models import Packet, Comment


def make_request(test_case, url, **kwargs):
    json_data = json.dumps(kwargs)
    return test_case.client.post(reverse(url), json_data, content_type="application/json")


def check_response_success(test_case, response):
    data = response.json()
    test_case.assertEqual(response.status_code, 200)
    test_case.assertEqual(data['success'], 'true')


def check_response_fail(test_case, response):
    data = response.json()
    test_case.assertEqual(response.status_code, 200)
    test_case.assertEqual(data['success'], 'false')


def add_user(username, password):
    user = User(username=username)
    user.set_password(password)
    user.save()
    return user


def new_packet(packet_name, content, lng, lat, delay, timeout):
    data = {}
    data['packet_name'] = packet_name
    data['content'] = content
    data['lng'] = lng
    data['lat'] = lat
    data['delay'] = delay
    data['timeout'] = timeout
    return json.dumps(data)


def do_login(self, username, password):
    data = {}
    data['username'] = username
    data['password'] = password
    json_data = json.dumps(data)
    self.client.post(reverse('login'), json_data, content_type="application/json")


class DropTest(TestCase):
    # [TODO] combine all the test cases together to simplify the code
    def test_drop_packet(self):
        # [TODO] easier way to write test cases
        # case1 drop packet with valid data
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        json_data = new_packet("test1", "test1_content", 123.4567890, 0.0, 0, -1)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        packet = Packet.objects.filter(creator=user1)[0]
        self.assertEqual(packet.name, 'test1')
        self.assertEqual(packet.content, 'test1_content')
        self.assertTrue(abs(packet.longitude - Decimal(123.4567890)) <= 0.00000001)
        self.assertTrue(abs(packet.latitude - 0) <= 0.00000001)

        # case2 drop packet with invalid longitude
        json_data = new_packet("test1", "test1_content", 180.001, 0.0, 0, -1)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        print response.json()['msg']
        self.assertEqual(response.json()['msg'], 'Invalid longitude')

        # case3 drop packet with invalid latitude
        json_data = new_packet("test1", "test1_content", 179, 90.1, 0, -1)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['msg'], 'Invalid latitude')

    def test_nearby_fetch_packet(self):
        # [TODO] the algorithm to fetch nearby packets is fake, need to be changed
        # [TODO] other test cases
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        json_data = new_packet("test1", "test1_content", 123.4567890, 0.0, 0, -1)
        self.client.post(reverse('drop'), json_data, content_type="application/json")

        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567890',
                'lat': '0.0'}
        json_data = json.dumps(data)
        response = self.client.post(reverse('get_nearby_packets'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertTrue(abs(Decimal(response.json()['data'][0]['lng']) - Decimal("123.4567890")) <= 0.00000001)
        self.assertTrue(abs(Decimal(response.json()['data'][0]['lat']) - Decimal("0.0")) <= 0.00000001)

    def test_pick_packet(self):
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        json_data = new_packet("test1", "test1_content", 123.4567890, 0.0, 0, -1)
        self.client.post(reverse('drop'), json_data, content_type="application/json")

        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0'
                }
        json_data = json.dumps(data)
        response = self.client.post(reverse('get_nearby_packets'), json_data, content_type="application/json")
        packet_id = response.json()['data'][0]['id']
        data = {'id': packet_id,
                'lng': '123.4567891',
                'lat': '0.0'
                }
        json_data = json.dumps(data)
        response = self.client.post(reverse('pick'), json_data, content_type="application/json")
        packet = Packet.objects.get(id=int(packet_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertEqual(response.json()['data']['packet_name'], 'test1')
        self.assertEqual(response.json()['data']['content'], 'test1_content')
        self.assertEqual(packet.owner, user2)

    def test_redrop_packet(self):
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        json_data = new_packet("test1", "test1_content", 123.4567890, 0.0, 0, -1)
        self.client.post(reverse('drop'), json_data, content_type="application/json")

        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0',
                }
        json_data = json.dumps(data)
        response = self.client.post(reverse('get_nearby_packets'), json_data, content_type="application/json")
        packet_id = response.json()['data'][0]['id']
        data = {'id': packet_id,
                'lng': '123.4567891',
                'lat': '0.0',}
        json_data = json.dumps(data)
        response = self.client.post(reverse('pick'), json_data, content_type="application/json")
        data = {'id': packet_id,
                'comment': "test_comment",
                'creator_only': 'flase',
                'ratings': 1}
        json_data = json.dumps(data)
        response = self.client.post(reverse('redrop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        comment = Comment.objects.filter(user=user2)[0]
        self.assertEqual(comment.packet.id, packet_id)
        self.assertEqual(comment.content, "test_comment")
        packet = Packet.objects.get(id=packet_id)
        self.assertEqual(packet.owner, None)

    def test_get_packet_details(self):
        # [TODO] refactor code below
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        json_data = new_packet("test1", "test1_content", 123.4567890, 0.0, 0, -1)
        self.client.post(reverse('drop'), json_data, content_type="application/json")

        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0',
                }
        json_data = json.dumps(data)
        response = self.client.post(reverse('get_nearby_packets'), json_data, content_type="application/json")
        packet_id = response.json()['data'][0]['id']
        data = {'id': packet_id,
                'lng': '123.4567891',
                'lat': '0.0',}
        json_data = json.dumps(data)
        response = self.client.post(reverse('pick'), json_data, content_type="application/json")
        data = {'id': packet_id,
                'comment': "test_comment",
                'creator_only': 'flase',
                'ratings': 1}
        json_data = json.dumps(data)
        response = self.client.post(reverse('redrop'), json_data, content_type="application/json")
        data = {'id': 1}
        json_data = json.dumps(data)
        response = self.client.post(reverse('get_packet_details'), json_data, content_type="application/json")
        right_response = {"msg": "Get packet details success",
                          "data": {"username": "user1", "credit": 100, "create_time": "2016-12-12", "likes": 1,
                                   "packet_name": "test1", "content": "test1_content", "dislikes": 0, "id": 1,
                                   "comments": [
                                       {"content": "test_comment", "username": "user2", "create_time": "2016-12-12"}]},
                          "success": "true"}

        # [TODO] Wait for credit and so on
        self.assertEqual(right_response, right_response)
        self.assertEqual(response.json()['data']['username'], "user1")
        self.assertEqual(response.json()['data']['likes'], 1)
        self.assertEqual(response.json()['data']['dislikes'], 0)
        self.assertEqual(response.json()['data']['comments'][0]['content'], "test_comment")


    # def test_ignore_packet(self):
    #     add_user("test_user1", "123456")
    #     add_user("test_user2", "123456")
    #
    #     make_request(test_case=self, url='login', username="test_user1", password="123456")
    #     make_request(test_case=self, url='drop', packet_name="test_packet_name1", content="test_content1",
    #                  lng=0, lat=0, delay=0, timeout=-1)
    #     make_request(test_case=self, url='drop', packet_name="test_packet_name1", content="test_content2",
    #                  lng=0, lat=0, delay=0, timeout=-1)
    #     r = make_request(test_case=self, url='drop', packet_name="test_packet_name1", content="test_content3",
    #                      lng=0, lat=0, delay=0, timeout=-1)
    #
    #     make_request(test_case=self, url='login', username="test_user2", password="123456")
    #     response = make_request(test_case=self, url='pick', id=Packet.objects.all()[1].id, lng=0, lat=0)
    #     # format[][][][][]
    #     # response = make_request(test_case=self, url='redrop', id=Packet.objects.all()[1].id, comment="test_comment", 'creator_only' = 'flase', 'ratings' = '1')
    #     # print response
    #     response = make_request(test_case=self, url='get_owning_packets', page_id=0)
    #     print(response.json())
    #     response = make_request(test_case=self, url='ignore', id=Packet.objects.all()[1].id)
    #     response = make_request(test_case=self, url='get_owning_packets', page_id=0)
    #     print(response.json())
    #     # response = make_request(test_case=self, url='redrop', id=Packet.objects.all()[0].id, comment="test_comment")
    #     response = make_request(test_case=self, url='get_owned_packets', page_id=0)
    #     print(response.json())
