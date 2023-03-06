import re
import datetime
from urllib.parse import urlparse
from unittest.mock import patch

from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, override_settings
from kombu.exceptions import OperationalError
from django.conf import settings

from core.users.models import User, UserPersonalProfile


class UserTests(APITestCase):
    users_passwords = {}
    random_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'\
        'eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjczNzM4MzI1LCJ'\
            'pYXQiOjE2NzM3MzcxMjUsImp0aSI6ImRiNmVlMjAzYmJlNDQ4Yj'\
                'E5ZDRkNzE1MDQ2MjYxNmQyIiwidXNlcl9pZCI6ImVkMTgwM'\
                    'jk3LWY0ZGYtNDFlYi05ZDc3LTBkZjFmZTBkMThhYSJ9'\
                        '.9Cyc5YFc-bs_lSprlJsLWsNY8h1THIDuVlO0lt'\
                            'skgm0'
    
    def obtain_token_pair(self, user):
        login_url = reverse('login')
        data = {
            'email': user.email,
            'password': self.users_passwords[user.username]
        }
        response = self.client.post(login_url, data, format='json')
        return response.data


    @classmethod
    def setUpTestData(cls) -> None:
        """
        10 users,
        user testuserone and testtusertwo are active.
        """
        cls.testuserone = User.objects.create_user(
            'testuserone@email.com',
            'testuserone',
            '6A37xvby&1!L'
            )
        cls.testuserone.is_active = True
        cls.testuserone.save()
        cls.users_passwords['testuserone'] = '6A37xvby&1!L'
        UserPersonalProfile(user=cls.testuserone).save()
        cls.testusertwo = User.objects.create_user(
            'testusertwo@email.com',
            'testusertwo',
            '6A37xvby&1!L'
        )
        cls.testusertwo.is_active = True
        cls.testusertwo.save()
        cls.users_passwords['testusertwo'] = '6A37xvby&1!L'
        UserPersonalProfile(user=cls.testusertwo).save()
        
        cls.user_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
        users = []
        for user_number in cls.user_numbers[2:]:
            user_password = User.objects.make_random_password()
            cls.users_passwords[f'testuser{user_number}'] = user_password
            users.append(User(
                email=f'testuser{user_number}@email.com', 
                username=f'testuser{user_number}',
                password=user_password))
        User.objects.bulk_create(users)
        return super().setUpTestData()

    def test_user_list(self):
        url = reverse('user-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 10)
        self.assertEqual(len(response.data['results']), 10)
    
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_create_user(self):
        """
        Ensure we can create a new User.
        """
        url = reverse('user-list')

        data = {
            'username': 'testusereleven',
            'email': 'testusereleven@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 11)
        self.assertEqual(User.objects.get(email='testusereleven@email.com').username, 'testusereleven')
        self.assertEqual(User.objects.get(email='testusereleven@email.com').is_active, False)

        data = {
            'username': 'testusertwelve',
            'email': 'testusertwelve@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 12)
        self.assertEqual(User.objects.get(email='testusertwelve@email.com').username, 'testusertwelve')
        self.assertEqual(User.objects.get(email='testusertwelve@email.com').is_active, False)

        self.assertEqual(len(mail.outbox), 2)

        # User shouldn't be created.

        with patch('core.users.tasks.email_message_task.delay') as mocked_email_message_task_delay:
            mocked_email_message_task_delay.side_effect = OperationalError
            data = {
                'username': 'testuserthirteen',
                'email': 'testuserthirteen@email.com',
                'password': '6A37xvby&1!L'
                }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertEqual(response.data['detail'], 'Service temporarily unavailable, try again later.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testusertwelve@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], 'user with this email address already exists.')

        data = {
            'username': 'testusertwelve',
            'email': 'testuserthirteen@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'user with this username already exists.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testuserthirteen@email',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testuserthirteenemail.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

        data = {
            'username': 'testuserthirteen' + ('x' * 32),
            'email': 'testuserthirteen@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['username'][0], 'Ensure this field has no more than 32 characters.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testuserthirteen@email.com',
            'password': 'testuserthirteen'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'The password is too similar to the username.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testuserthirteen@email.com',
            "password": "password"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'This password is too common.')

        data = {
            'username': 'testuserthirteen',
            'email': 'testuserthirteen@email.com',
            "password": "passwor"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'This password is too short. It must contain at least 8 characters.')


    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_token_activate_user(self):
        url = reverse('user-list')
        data = {
            'username': 'testusereleven',
            'email': 'testusereleven@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(User.objects.get(email='testusereleven@email.com').is_active, False)

        url = reverse('user-token-activate-user')
        body = mail.outbox[0].body
        links = re.findall(r'(https?://\S+)', body)
        activation_link_url = None
        for link in links:
            parsed_url = urlparse(link)
            if parsed_url.query:
                activation_link_url = url + '?' + parsed_url.query
                break     

        if activation_link_url:
            # let's make sure that the token won't work after the timeout
            with patch('core.users.utils.tokens.ActivateUserTokenGenerator._now') as mocked__now:
                mocked__now.return_value = datetime.datetime.now() + datetime.timedelta(0, settings.PASSWORD_RESET_TIMEOUT+60)
                response = self.client.get(activation_link_url, format='json')
                self.assertEqual(response.status_code, 400)
            
            response = self.client.get(activation_link_url, format='json')
            self.assertEqual(response.status_code, 200)
            # it's not possible to use this link/activate the user twice
            response = self.client.get(activation_link_url, format='json')
            self.assertEqual(response.status_code, 400)
        else:
            raise TypeError("Link doesn't exist")

        self.assertEqual(User.objects.get(email='testusereleven@email.com').is_active, True)

    def test_user_detail(self):
        url = reverse('user-detail', kwargs={"pk": str(self.testuserone.id)})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.random_access_token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('detail', 'no detail'), 'Given token not valid for any token type')

        token_pair = self.obtain_token_pair(self.testuserone)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username', 'no username'), 'testuserone')
        self.assertEqual(response.data.get('email', 'no email'), 'testuserone@email.com')

        # testusertwo makes the request on behalf of testuserone
        token_pair = self.obtain_token_pair(self.testusertwo)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_user_update(self):
        """
        PUT method
        """
        url = reverse('user-detail', kwargs={"pk": str(self.testuserone.id)})
        response = self.client.put(url, format='json')
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        token_pair = self.obtain_token_pair(self.testuserone)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
    
    def test_user_partial_update(self):
        """
        PATCH method
        """
        url = reverse('user-detail', kwargs={"pk": str(self.testuserone.id)})
        response = self.client.patch(url, format='json')
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # testusertwo makes the request on behalf of testuserone
        token_pair = self.obtain_token_pair(self.testusertwo)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        data = {
            "username": "testuserone",
            "email": "testuserone@email.com",
            "password": "8B33xvby&1!R"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.random_access_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data.get('detail', 'no detail'), 'Given token not valid for any token type')
        
        token_pair = self.obtain_token_pair(self.testuserone)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        data = {
            "username": "testuseroneupdated",
            "email": "testuseroneupdated@email.com",
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        # email address and username can't be changed
        self.assertEqual(response.data['username'], 'testuserone')
        self.assertEqual(response.data['email'], 'testuserone@email.com')

        data = {
            "password": "password"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'This password is too common.')

        data = {
            "password": "passwor"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'This password is too short. It must contain at least 8 characters.')

        data = {
            "password": "testuserone"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['password'][0], 'The password is too similar to the username.')

        data = {
            "password": "8B33xvby&1!R"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('password', 'no password'), 'no password')
        testuserone_updated = User.objects.get(email="testuserone@email.com")
        self.assertNotEqual(self.testuserone.password, testuserone_updated.password)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_token_password_reset(self):
        url = reverse('user-token-password-reset')
        
        data = {
	        "email": "testuserthriteen@email.com"
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Not found.')

        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], 'This field is required.')
        
        data = {
	        "email": "testuserone@email.com"
            }
        response = self.client.post(url, data, format='json')

        body = mail.outbox[0].body
        links = re.findall(r'(https?://\S+)', body)
        password_reset_link = None
        for link in links:
            parsed_url = urlparse(link)
            if parsed_url.query:
                password_reset_link = url + '?' + parsed_url.query
                break
        
        if password_reset_link:
            data = {}
            response = self.client.patch(password_reset_link, data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['password'][0], 'This field is required.')
            
            data = {
                "password": "testuserone"
            }
            response = self.client.patch(password_reset_link, data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['password'][0], 'The password is too similar to the username.')

            data = {
                "password": "testuserone@email.com"
            }
            response = self.client.patch(password_reset_link, data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['password'][0], 'The password is too similar to the email address.')

            # let's make sure that the token won't work after the timeout
            with patch('core.users.utils.tokens.CustomPasswordResetTokenGenerator._now') as mocked__now:
                mocked__now.return_value = datetime.datetime.now() + datetime.timedelta(0, settings.PASSWORD_RESET_TIMEOUT+60)
                response = self.client.patch(password_reset_link, data, format='json')
                self.assertEqual(response.status_code, 400)
            
            data = {
                "password": "7C34xvby&1!A"
            }
            response = self.client.patch(password_reset_link, data, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, None)
            
            # password reset link can be used only once
            data = {
                "password": "7C34xvby&1!A"
            }
            response = self.client.patch(password_reset_link, data, format='json')
            self.assertEqual(response.status_code, 400)

            testuserone_updated = User.objects.get(email='testuserone@email.com')
            self.assertNotEqual(self.testuserone.password, testuserone_updated.password)

            # let's try to log in with the old and new password
            login_url = reverse('login')
            data = {
                'email': 'testuserone@email.com',
                'password': self.users_passwords['testuserone']
            }
            response = self.client.post(login_url, data, format='json')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
            
            login_url = reverse('login')
            data = {
                'email': 'testuserone@email.com',
                'password': "7C34xvby&1!A"
            }
            response = self.client.post(login_url, data, format='json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('access', response.data)

        else:
            raise TypeError("Link doesn't exist")



        
