import json
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class LoginTest(TestCase):
    
    def test_valid_login_(self):
        """
        ensure user_login returns correct json format data when user authentification is correct
        """
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '1234567890'
        json_data = json.dumps(data)
        response = self.client.post(reverse('login'), json_data, content_type="applicaton/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertEqual(response.json()['data'], {})
        self.assertEqual(response.json()['msg'], 'Login success')

    def test_invalid_login(self):
        """
        ensure user_login returns correct json format data when user authentification is incorrect
        """
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '12345678'
        json_data = json.dumps(data)
        response = self.client.post(reverse('login'), json_data, content_type="applicaton/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['data'], {})
        self.assertEqual(response.json()['msg'], 'Password incorrect')
        
