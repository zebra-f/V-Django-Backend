from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
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

        data = {
            'username': 'testusertwelve',
            'email': 'testusertwelve@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 12)
        self.assertEqual(User.objects.get(email='testusertwelve@email.com').username, 'testusertwelve')

        # testuserthirteen won't be created

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
