from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, override_settings
from ..models import Speed
from django.contrib.auth import get_user_model


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
    fixtures = ["core/speeds/fixtures/test_fixtures.json"]

    # @classmethod
    # def setUpTestData(cls) -> None:
    #     pass

    def setUp(self):
        print("aaa")
        self.author = User.objects.create_user(
            username="test_author",
            email="author@example.com",
            password="password",
        )
        self.data = {
            "name": "Test Speed",
            "description": "Test Speed Description",
            "tags": "test, speed, drf",
            "kmph": 100,
            "author": self.author.id,
            "public": True,
        }

    # def test_create_speed(self):
    #     self.client.force_login(self.author)
    #     response = self.client.post(reverse("speed-list"), self.data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Speed.objects.count(), 1)
    #     self.assertEqual(Speed.objects.get().name, self.data["name"])

    def test_update_speed_detail(self):
        print("aaaaaaaaaaaaaa")
        url = reverse("speed-list")
        response = self.client.get(url)
        print(response)
        print(response.data)
        print("bbbbbbbbbbbbbb--------------\n\n")

        # data = {
        #     "name": "New Name",
        #     "description": "New Description",
        #     "tags": "new, tags, drf",
        #     "kmph": 150,
        #     "public": False,
        # }
        # self.client.force_login(self.author)
        # response = self.client.put(self.url, data)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.speed.refresh_from_db()
        # self.assertEqual(self.speed.name, data["name"])
        # self.assertEqual(self.speed.description, data["description"])
        # self.assertEqual(self.speed.tags, data["tags"])
        # self.assertEqual(self.speed.kmph, data["kmph"])
        # self.assertEqual(self.speed.public, data["public"])
