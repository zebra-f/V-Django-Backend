from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.users.models import User, UserPersonalProfile


class UserTests(APITestCase):
    users_passwords = {}
    random_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\
        .eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjczNzM4MzI1LC\
            JpYXQiOjE2NzM3MzcxMjUsImp0aSI6ImRiNmVlMjAzYmJlNDQ4Y\
                jE5ZDRkNzE1MDQ2MjYxNmQyIiwidXNlcl9pZCI6ImVkMTgw\
                    Mjk3LWY0ZGYtNDFlYi05ZDc3LTBkZjFmZTBkMThhYSJ\
                        9.9Cyc5YFc-bs_lSprlJsLWsNY8h1THIDuVlO0l\
                            tskgm0'

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
        8 users,
        user userone and tuserwo are active.
        """
        cls.userone = User.objects.create_user(
            'testuserone@email.com',
            'testuserone',
            '6A37xvby&1!L'
            )
        cls.userone.is_active = True
        cls.userone.save()
        cls.users_passwords['testuserone'] = '6A37xvby&1!L'
        UserPersonalProfile(user=cls.userone).save()
        cls.usertwo = User.objects.create_user(
            'testusertwo@email.com',
            'testusertwo',
            '6A37xvby&1!L'
        )
        cls.usertwo.is_active = True
        cls.usertwo.save()
        cls.users_passwords['testusertwo'] = '6A37xvby&1!L'
        UserPersonalProfile(user=cls.usertwo).save()
        
        cls.user_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
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


    def test_create_user(self):
        """
        Ensure we can create a new User.
        """
        url = reverse('user-list')

        data = {
            'username': 'testusernine',
            'email': 'testusernine@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 9)
        self.assertEqual(User.objects.get(email='testusernine@email.com').username, 'testusernine')

        data = {
            'username': 'testuserten',
            'email': 'testuserten@email.com',
            'password': '6A37xvby&1!L'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 10)
        self.assertEqual(User.objects.get(email='testuserten@email.com').username, 'testuserten')

    def test_user_detail(self):
        url = reverse('user-detail', kwargs={"pk": str(self.userone.id)})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.random_access_token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        token_pair = self.obtain_token_pair(self.userone)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_pair['access'])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
