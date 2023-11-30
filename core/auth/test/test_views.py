from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from core.users.models import User, UserPersonalProfile


class AuthTests(APITestCase):
    users_passwords = {}
    random_access_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjczNzM4MzI1LCJ"
        "pYXQiOjE2NzM3MzcxMjUsImp0aSI6ImRiNmVlMjAzYmJlNDQ4YjE5ZDR"
        "kNzE1MDQ2MjYxNmQyIiwidXNlcl9pZCI6ImVkMTgwMjk3LWY0ZGYtNDF"
        "lYi05ZDc3LTBkZjFmZTBkMThhYSJ9"
        ".9Cyc5YFc-bs_lSprlJsLWsNY8h1THIDuVlO0ltskgm0"
    )

    def setUp(self) -> None:
        self.testadmin = User.objects.create_superuser(
            username="testadminone",
            email="testadminone@email.com",
            password="6A37xvby&1!L",
        )
        return super().setUp()

    @classmethod
    def setUpTestData(cls) -> None:
        """
        10 users,
        user testuserone and testtusertwo are active.
        """
        cls.testuserone = User.objects.create_user(
            "testuserone@email.com", "testuserone", "6A37xvby&1!L"
        )
        cls.testuserone.is_active = True
        cls.testuserone.email_verified = True
        cls.testuserone.save()
        cls.users_passwords["testuserone"] = "6A37xvby&1!L"
        UserPersonalProfile(user=cls.testuserone).save()
        cls.testusertwo = User.objects.create_user(
            "testusertwo@email.com", "testusertwo", "6A37xvby&1!L"
        )
        cls.testusertwo.is_active = True
        cls.testusertwo.email_verified = True
        cls.testusertwo.save()
        cls.users_passwords["testusertwo"] = "6A37xvby&1!L"
        UserPersonalProfile(user=cls.testusertwo).save()

        cls.user_numbers = [
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
        ]
        users = []
        for user_number in cls.user_numbers[2:]:
            user_password = User.objects.make_random_password()
            cls.users_passwords[f"testuser{user_number}"] = user_password
            users.append(
                User(
                    email=f"testuser{user_number}@email.com",
                    username=f"testuser{user_number}",
                    password=user_password,
                )
            )
        User.objects.bulk_create(users)
        return super().setUpTestData()

    def test_login(self):
        url = reverse("login")

        users = User.objects.all()
        for user in users:
            if user == self.testadmin:
                continue

            user_last_login = user.last_login
            self.assertEqual(user_last_login, None)

            data = {
                "email": user.email,
                "password": self.users_passwords[user.username],
            }
            response = self.client.post(url, data, format="json")
            if user.is_active and user.email_verified:
                self.assertEqual(response.status_code, 200)

                # check whether `refresh` token was
                # deleted and only `access` token is returned
                self.assertEqual(len(response.data), 1)
                self.assertEqual(list(response.data.keys()), ["access"])
                self.assertEqual(len(response.cookies.keys()), 1)
                # check whether `refresh` token was set (correctly) as a cookie
                for cookie, morsel_instance in response.cookies.items():
                    if str(cookie) != "refresh":
                        raise AttributeError()
                    self.assertEqual(len(morsel_instance.value), 279)
                    self.assertEqual(len(morsel_instance.value.split(".")), 3)

                    path = morsel_instance["path"]
                    max_age = morsel_instance["max-age"]
                    httponly = morsel_instance["httponly"]
                    samesite = morsel_instance["samesite"]
                    self.assertEqual(path, "/api/token/")
                    self.assertEqual(
                        max_age,
                        settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].days
                        * 24
                        * 60
                        * 60,
                    )
                    self.assertEqual(httponly, True)
                    self.assertEqual(samesite, "Strict")

                # try to use the access token as authentication method
                access_token = response.data["access"]
                whoami_url = reverse("user-whoami")

                # correct token
                self.client.credentials(
                    HTTP_AUTHORIZATION="Bearer " + access_token
                )
                response = self.client.get(whoami_url, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # check if user has logged in
                user_ = User.objects.get(pk=user.pk)
                self.assertNotEqual(user_last_login, user_.last_login)

                # incorrect token
                self.client.credentials(
                    HTTP_AUTHORIZATION="Bearer " + self.random_access_token
                )
                response = self.client.get(whoami_url, format="json")
                self.assertEqual(
                    response.status_code, status.HTTP_403_FORBIDDEN
                )
            else:
                self.assertEqual(response.status_code, 401)
                self.assertEqual(
                    response.data["detail"],
                    "No active account found with the given credentials",
                )

    def test_logout(self):
        url = reverse("logout")

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 401)

        blacklisted_tokens_counter = 0
        for user in [self.testuserone, self.testusertwo]:
            # log in a user, returns/sets refresh token cookie
            data = {
                "email": user.email,
                "password": self.users_passwords[user.username],
            }
            response = self.client.post(reverse("login"), data, format="json")

            cookies = response.cookies

            self.client.credentials(
                HTTP_AUTHORIZATION="Bearer " + response.data["access"]
            )

            # try to log out
            del self.client.cookies["refresh"]
            # data sent as `JSON` should be ignored
            data = {"refresh": cookies["refresh"].value}
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(
                response.data["detail"],
                "No valid refresh token has been found in cookies.",
            )

            blacklisted_tokens = BlacklistedToken.objects.all()
            self.assertEqual(
                len(blacklisted_tokens), blacklisted_tokens_counter
            )

            self.client.cookies["refresh"] = cookies["refresh"]
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, 200)

            blacklisted_tokens = BlacklistedToken.objects.all()
            blacklisted_tokens_counter += 1
            self.assertEqual(
                len(blacklisted_tokens), blacklisted_tokens_counter
            )

    def test_refresh(self):
        url = reverse("refresh")

        response = self.client.post(url, {}, format="json")
        # refresh endpoint doesn't require a user to be aunthenticated
        self.assertEqual(response.status_code, 404)

        # # log in a user, returns/sets refresh token cookie
        data = {
            "email": self.testuserone.email,
            "password": self.users_passwords[self.testuserone.username],
        }
        response = self.client.post(reverse("login"), data, format="json")

        cookies = response.cookies
        prev_access_token = response.data["access"]

        # try to refresh
        del self.client.cookies["refresh"]
        # data sent as `JSON` should be ignored
        data = {"refresh": cookies["refresh"].value}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["detail"],
            "No valid refresh token has been found in cookies.",
        )

        self.client.cookies["refresh"] = cookies["refresh"]
        for _ in range(4):
            response = self.client.post(url, data, format="json")
            self.assertEqual(response.status_code, 200)
            if "access" not in response.data:
                raise AttributeError("Access token was not returned.")

            self.assertNotEqual(response.data["access"], prev_access_token)
            prev_access_token = response.data["access"]

            # ensure that refresh token is not rotated
            self.assertEqual(self.client.cookies, cookies)
            blacklisted_tokens = BlacklistedToken.objects.all()
            self.assertEqual(len(blacklisted_tokens), 0)
