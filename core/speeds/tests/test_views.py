from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, override_settings

from ..models import Speed


User = get_user_model()

# testuserone and testusertwo password- 6A37xvby&1!L

# testuserone likes testusertwo name two  "d26c8bad-6548-4918-8e63-1bd59579917b"
# testuserone dislikes testusertwo name three "67e77deb-13d5-43fa-af9f-cc6f1b2a1c5c"
# testuserone bookmarked testusertwo name three

# testusertwo dislikes testuserone name one "706efb42-5d91-4115-a52b-3e0c98fb8cd5"
# testusertwo reported testuserone name two "66fca277-3329-49aa-96a2-cc240a659549"


@override_settings(
    MEILISEARCH={"disabled": True, "MASTER_KEY": None, "URL": None}
)
class SpeedTests(APITestCase):
    fixtures = ["speeds_tests_fixtures.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        return super().setUpTestData()

    def setUp(self):
        self.testuserone = User.objects.get(username="testuserone")
        self.testusertwo = User.objects.get(username="testusertwo")
        return super().setUp()

    def obtain_token_pair(self, user):
        login_url = reverse("login")
        data = {
            "email": user.email,
            "password": self.users_passwords[user.username],
        }
        response = self.client.post(login_url, data, format="json")
        return response.data

    def test_speed_list(self):
        url = reverse("speed-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 5
        )
        for speed in response.data["results"]:
            self.assertEqual(speed["is_public"], True)

        self.client.force_login(self.testuserone)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 6
        )
        for speed in response.data["results"]:
            if speed["is_public"] == False:
                self.assertEqual(speed["user"], self.testuserone.username)

        self.client.force_login(self.testusertwo)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 5
        )
