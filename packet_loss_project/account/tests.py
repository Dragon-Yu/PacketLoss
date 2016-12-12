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
        response = self.client.post(reverse('login'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertEqual(response.json()['data'], {})
        self.assertEqual(response.json()['msg'], 'Login success')

    def test_invalid_login(self):
        """
        ensure user_login returns correct json format data when user authentification is incorrect
        [TODO] other kinds of invalid login information
        """
        # test case 1 (incorrect password)
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '12345678'
        json_data = json.dumps(data)
        response = self.client.post(reverse('login'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['data'], {})
        self.assertEqual(response.json()['msg'], 'Password incorrect')
        # [TODO] other kinds of invalid login information


class RegisterTest(TestCase):
    def test_valid_register(self):
        """
        ensure register returns correct json format data if register information is valid
        """
        data = {}
        data['username'] = 'user1'
        data['password'] = '1234567890'
        json_data = json.dumps(data)
        response = self.client.post(reverse('register'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')
        self.assertEqual(response.json()['data'], {})
        self.assertEqual(response.json()['msg'], 'Register success')
        User.objects.get(username="user1")

    def test_invalid_register(self):
        """
        test several invalid register cases:
        1. user already exist
        2. username not valid
        3. userpassword not valid
        """
        # test case 1
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '12345678'
        json_data = json.dumps(data)
        response = self.client.post(reverse('register'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(len(User.objects.filter(username='user1')), 1)

        # test case 2
        data = {}
        data['username'] = 'select * from'
        data['password'] = '12345678'
        json_data = json.dumps(data)
        response = self.client.post(reverse('register'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(len(User.objects.filter(username='select * from')), 0)

        # test case 3
        data ={}
        data['username'] = 'user2'
        data['password'] = ''
        json_data = json.dumps(data)
        response = self.client.post(reverse('register'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(len(User.objects.filter(username='user2')), 0)


class LogoutTest(TestCase):
    def test_logout(self):
        """
        RT, also a test for @login_required decorator
        """
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '1234567890'
        json_data = json.dumps(data)
        self.client.post(reverse('login'), json_data, content_type="application/json")

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'false')
        self.assertEqual(response.json()['msg'], 'Please login first')


class ChangePasswordTest(TestCase):
    def test_change_password(self):
        """
        RT
        """
        user1 = User(username='user1')
        user1.set_password('1234567890')
        user1.save()
        data = {}
        data['username'] = 'user1'
        data['password'] = '1234567890'
        json_data = json.dumps(data)
        self.client.post(reverse('login'), json_data, content_type="application/json")

        data['old_password'] = '1234567890'
        data['new_password'] = '1234567890aAa'
        json_data = json.dumps(data)
        response = self.client.post(reverse('password'), json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'true')

        data['username'] = 'user1'
        data['password'] = '1234567890'
        json_data = json.dumps(data)
        response = self.client.post(reverse('login'), json_data, content_type="application/json")
        self.assertEqual(response.json()['success'], 'false')

        data['username'] = 'user1'
        data['password'] = '1234567890aAa'
        json_data = json.dumps(data)
        response = self.client.post(reverse('login'), json_data, content_type="application/json")
        self.assertEqual(response.json()['success'], 'true')
