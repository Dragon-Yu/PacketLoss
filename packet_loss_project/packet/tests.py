import json
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from packet.models import Packet, Comment

def add_user(username, password):
    user = User(username=username)
    user.set_password(password)
    user.save()
    return user

def do_login(test_case, username, password):
    data = {}
    data['username'] = username
    data['password'] = password
    json_data = json.dumps(data)
    test_case.client.post(reverse('login'), json_data, content_type="application/json")

class DropTest(TestCase):
    # [TODO] combine all the test cases together to simplify the code
    def test_drop_packet(self):
        # [TODO] easier way to write test cases
        # case1 drop packet with valid data
        user1 = add_user('user1', '1234567890')        
        do_login(self, 'user1', '1234567890')
        data = {}
        data['packet_name'] = "test1"
        data['content'] = "test1_content"
        data['lng'] = "123.4567890"
        data['lat'] = "0.0"
        json_data = json.dumps(data)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        packet = Packet.objects.filter(creator=user1)[0]
        self.assertEqual(packet.name, 'test1')
        self.assertEqual(packet.content, 'test1_content')
        self.assertTrue(abs(packet.longitude-Decimal(123.4567890)) <= 0.00000001)
        self.assertTrue(abs(packet.latitude-0) <= 0.00000001)

        # case2 drop packet with invalid longitude
        data['lng'] = "180.123"
        data['lat'] = "20"
        json_data = json.dumps(data)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['msg'], 'Invalid longitude or latitude')

        # case3 drop packet with invalid latitude
        data['lng'] = "120"
        data['lat'] = "-90.00001"
        json_data = json.dumps(data)
        response = self.client.post(reverse('drop'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['msg'], 'Invalid longitude or latitude')

    def test_nearby_fetch_packet(self):
        # [TODO] the algorithm to fetch nearby packets is fake, need to be changed
        # [TODO] other test cases
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        data = {}
        data['packet_name'] = "test1"
        data['content'] = "test1_content"
        data['lng'] = "123.4567890"
        data['lat'] = "0.0"
        json_data = json.dumps(data)
        self.client.post(reverse('drop'), json_data, content_type="application/json")
        
        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0', }
        json_data = json.dumps(data)
        response = self.client.post(reverse('fetch'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertTrue(abs(Decimal(response.json()['data'][0]['lng']) - Decimal("123.4567890")) <= 0.00000001)
        self.assertTrue(abs(Decimal(response.json()['data'][0]['lat']) - Decimal("0.0")) <= 0.00000001)

    def test_pick_packet(self):
        user1 = add_user('user1', '1234567890')
        do_login(self, 'user1', '1234567890')
        data = {}
        data['packet_name'] = "test1"
        data['content'] = "test1_content"
        data['lng'] = "123.4567890"
        data['lat'] = "0.0"
        json_data = json.dumps(data)
        self.client.post(reverse('drop'), json_data, content_type="application/json")
        
        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0', }
        json_data = json.dumps(data)
        response = self.client.post(reverse('fetch'), json_data, content_type="application/json")
        packet_id = response.json()['data'][0]['id']
        data = {'id': packet_id}
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
        data = {}
        data['packet_name'] = "test1"
        data['content'] = "test1_content"
        data['lng'] = "123.4567890"
        data['lat'] = "0.0"
        json_data = json.dumps(data)
        self.client.post(reverse('drop'), json_data, content_type="application/json")
        
        user2 = add_user('user2', '1234567890')
        do_login(self, 'user2', '1234567890')
        data = {'lng': '123.4567891',
                'lat': '0.0', }
        json_data = json.dumps(data)
        response = self.client.post(reverse('fetch'), json_data, content_type="application/json")
        packet_id = response.json()['data'][0]['id']
        data = {'id': packet_id}
        json_data = json.dumps(data)
        response = self.client.post(reverse('pick'), json_data, content_type="application/json")
        data = {'id': packet_id,
                'comment': "test_comment",}
        json_data = json.dumps(data)
        response = self.client.post(reverse('redrop'), json_data, content_type="application/json")        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        comment = Comment.objects.filter(user=user2)[0]
        self.assertEqual(comment.packet.id, packet_id)
        self.assertEqual(comment.content, "test_comment")
        packet = Packet.objects.get(id=packet_id)
        self.assertEqual(packet.owner, None)
