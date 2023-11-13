import string

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
    MEILISEARCH={"disabled": True, "MASTER_KEY": None, "URL": None},
)
class SpeedTests(APITestCase):
    fixtures = ["speeds_tests_fixture"]

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

    def test_speed_retrieve(self):
        speeds = Speed.objects.all()
        for speed in speeds:
            url = reverse("speed-detail", kwargs={"pk": str(speed.pk)})
            response = self.client.get(url)
            if speed.is_public == True:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["id"], str(speed.pk))
                self.assertEqual(len(response.data), 11)
            else:
                self.assertEqual(response.status_code, 404)

        self.client.force_login(self.testuserone)
        for speed in speeds:
            if speed.user == self.testuserone:
                url = reverse("speed-detail", kwargs={"pk": str(speed.pk)})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.data["user"], self.testuserone.username
                )

        self.client.force_login(self.testusertwo)
        for speed in speeds:
            url = reverse("speed-detail", kwargs={"pk": str(speed.pk)})
            response = self.client.get(url)
            if speed.user != self.testusertwo:
                if speed.is_public == False:
                    self.assertEqual(response.status_code, 404)
                    continue
            self.assertEqual(response.status_code, 200)
            # 2 more fields for a logged in user
            self.assertEqual(len(response.data), 13)
            if "user_speed_feedback" not in response.data:
                raise self.failureException(
                    "`user_speed_feedback` was not found in response' data."
                )
            if "user_speed_bookmark" not in response.data:
                raise self.failureException(
                    "`user_speed_feedback` was not found in response' data."
                )

    def test_speed_create(self):
        url = reverse("speed-list")
        data = {
            "name": "anon name one",
            "description": "anon description one",
            "speed_type": "relative",
            "tags": ["three", "four", "nine"],
            "kmph": 1.0,
            "estimated": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        self.client.force_login(self.testuserone)
        data = {
            # "name": "testuserone name four",
            # "description": "testuserone description four",
            # "speed_type": "relative",
            # "tags": ["three", "four", "nine"],
            # "kmph": 4.0,
            # "estimated": False,
            # "is_public": True,
        }
        response = self.client.post(url, data, format="json")
        required_fields = {
            "name",
            "description",
            "speed_type",
            "kmph",
            "tags",
        }
        self.assertEqual(response.status_code, 400)
        for field, message in response.data.items():
            self.assertEqual(message[0], "This field is required.")
            required_fields.remove(field)
        self.assertEqual(len(required_fields), 0)

        data = {
            "name": "testuserone name four",
            "description": "testuserone description four",
            "speed_type": "relative",
            "tags": ["three", "four", "nine"],
            "kmph": 4.0,
            "estimated": False,
            "is_public": False,
        }
        valid_name_chars = {"'", "-", "_"}
        valid_description_chars = {",", "'", ".", "-", '"', ".", "(", ")", ","}
        valid_tags_chars = {"'", "-"}
        for char in string.punctuation:
            data["name"] += char
            response = self.client.post(url, data, format="json")
            if char not in valid_name_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 201)
            data["name"] = data["name"][0 : len(data["name"]) - 1]

            data["description"] += char
            response = self.client.post(url, data, format="json")
            if char not in valid_description_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 201)
            data["description"] = data["description"][
                0 : len(data["description"]) - 1
            ]

            data["tags"].append("ten" + char)
            response = self.client.post(url, data, format="json")
            if char not in valid_tags_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 201)
            data["tags"].pop()

        data = {
            "name": "t",
            "description": "t" * 7,
            "speed_type": "relative",
            "tags": ["three", "four", "nine", "ten", "eleven"],
            "kmph": 4.0,
            "estimated": False,
            "is_public": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.data), 3)

        data = {
            "name": "testuserone name four",
            "description": "testuserone description four",
            "speed_type": "relative",
            "tags": ["three", "four", "nine"],
            "kmph": 4.0,
            "estimated": False,
            "is_public": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
