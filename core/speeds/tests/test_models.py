import random
from unittest.mock import patch
from collections import defaultdict

from django.contrib.auth import get_user_model

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
class CustomAPITestCase(APITestCase):
    """
    Disables Meilisearch integration and Celery workers to
    prevent data synchronization attempts in some tests.
    """

    fixtures = ["speeds_tests_fixture"]

    @classmethod
    def setUpClass(cls) -> None:
        ret = super().setUpClass()
        cls.patcher_delay = patch("celery.app.task.Task.delay", return_value=1)
        cls.mock_delay = cls.patcher_delay.start()
        return ret

    @classmethod
    def tearDownClass(cls) -> None:
        ret = super().tearDownClass()
        cls.patcher_delay.stop()
        return ret

    @classmethod
    def setUpTestData(cls) -> None:
        return super().setUpTestData()

    def setUp(self):
        self.testuserone = User.objects.get(username="testuserone")
        self.testusertwo = User.objects.get(username="testusertwo")
        return super().setUp()


class SpeedTestCase(CustomAPITestCase):
    def test_recount_votes(self):
        for speed in Speed.objects.all():
            curr_score = speed.score
            curr_upvotes = speed.upvotes
            curr_downvotes = speed.downvotes

            speed.score = random.randint(-1000, 1000)
            speed.downvotes = random.randint(0, 1000)
            speed.upvotes = random.randint(0, 1000)
            speed.save()

            speed.recount_votes()

            self.assertEqual(speed.score, curr_score)
            self.assertEqual(speed.upvotes, curr_upvotes)
            self.assertEqual(speed.downvotes, curr_downvotes)

    def test_recount_all_votes(self):
        cache = defaultdict(dict)

        for speed in Speed.objects.all():
            cache[str(speed.id)]["score"] = speed.score
            cache[str(speed.id)]["upvotes"] = speed.upvotes
            cache[str(speed.id)]["downvotes"] = speed.downvotes

            speed.score = random.randint(-1000, 1000)
            speed.downvotes = random.randint(0, 1000)
            speed.upvotes = random.randint(0, 1000)
            speed.save()

        Speed.recount_all_votes()

        for speed in Speed.objects.all():
            self.assertEqual(speed.score, cache[str(speed.id)]["score"])
            self.assertEqual(speed.upvotes, cache[str(speed.id)]["upvotes"])
            self.assertEqual(
                speed.downvotes, cache[str(speed.id)]["downvotes"]
            )
