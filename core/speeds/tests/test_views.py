import string
from unittest.mock import patch

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.db import transaction

from rest_framework.test import APITestCase, override_settings

from ..models import Speed, SpeedFeedback


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

    def obtain_token_pair(self, user):
        login_url = reverse("login")
        data = {
            "email": user.email,
            "password": self.users_passwords[user.username],
        }
        response = self.client.post(login_url, data, format="json")
        return response.data


class SpeedTests(CustomAPITestCase):
    valid_name_chars = {"'", "-", "_"}
    valid_description_chars = {",", "'", ".", "-", '"', ".", "(", ")", ","}
    valid_tags_chars = {"'", "-"}

    def test_speed_list(self):
        url = reverse("speed-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 5
        )
        for speed in response.data["results"]:
            self.assertEqual(speed["is_public"], True)
        # query params (anon)
        response = self.client.get(url, {"is_public": False})
        self.assertEqual(len(response.data["results"]), 0)
        response = self.client.get(url, {"tags": "three"})
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(url, {"tags": "one,seven"})
        self.assertEqual(len(response.data["results"]), 1)
        for char in string.punctuation:
            response = self.client.get(url, {"tags": f"one{char}"})
            if char not in self.valid_tags_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 200)
        response = self.client.get(url, {"user": "testuserone"})
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get(url, {"user": "testusertwo"})
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 3
        )
        response = self.client.get(url, {"user": "testusertwo", "tags": "one"})
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(url, {"tags": "one"})
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 2
        )

        self.client.force_login(self.testuserone)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 6
        )
        for speed in response.data["results"]:
            if speed["is_public"] == False:
                self.assertEqual(speed["user"], self.testuserone.username)
        # query params (testuserone)
        response = self.client.get(url, {"is_public": False})
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(url, {"tags": "three"})
        self.assertEqual(len(response.data["results"]), 2)
        response = self.client.get(url, {"tags": "one,seven"})
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(url, {"user": "testuserone"})
        self.assertEqual(response.data["count"], 3)

        self.client.force_login(self.testusertwo)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data["results"]), response.data["count"], 5
        )
        # query params (testusertwo)
        response = self.client.get(url, {"is_public": False})
        self.assertEqual(len(response.data["results"]), 0)
        response = self.client.get(url, {"tags": "three"})
        self.assertEqual(len(response.data["results"]), 1)
        response = self.client.get(url, {"tags": "one,seven"})
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(url, {"user": "testuserone"})
        self.assertEqual(response.data["count"], 2)

    def test_personal_list(self):
        url = reverse("speed-personal-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        self.client.force_login(self.testuserone)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        for result in response.data["results"]:
            self.assertEqual(result["user"], "testuserone")

        self.client.force_login(self.testusertwo)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)
        for result in response.data["results"]:
            self.assertEqual(result["user"], "testusertwo")

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

        for char in string.punctuation:
            data["name"] += char
            response = self.client.post(url, data, format="json")
            if char not in self.valid_name_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 201)
            data["name"] = data["name"][0 : len(data["name"]) - 1]

            data["description"] += char
            response = self.client.post(url, data, format="json")
            if char not in self.valid_description_chars:
                self.assertEqual(response.status_code, 400)
            else:
                self.assertEqual(response.status_code, 201)
            data["description"] = data["description"][
                0 : len(data["description"]) - 1
            ]

            data["tags"].append("ten" + char)
            response = self.client.post(url, data, format="json")
            if char not in self.valid_tags_chars:
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

    def test_speed_update(self):
        for speed in self.testuserone.speed_set.all():
            url = reverse("speed-detail", kwargs={"pk": str(speed.id)})
            data = {
                "name": f"{speed.name} updated",
                "description": f"{speed.description} updated",
                "speed_type": "relative",
                "tags": ["three", "four", "nine"],
                "kmph": 4.0,
                "estimated": False,
                "is_public": False,
            }

            self.client.logout()
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            self.client.force_login(self.testusertwo)
            response = self.client.put(url, data, format="json")
            if not speed.is_public:
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.data["detail"],
                    "Not found.",
                )
            else:
                self.assertEqual(response.status_code, 403)
                self.assertEqual(
                    response.data["detail"],
                    "You do not have permission to perform this action.",
                )

            self.client.force_login(self.testuserone)
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["name"], speed.name + " updated")
            self.assertEqual(
                response.data["description"], speed.description + " updated"
            )
            data = {
                "name": f"{speed.name} updated updated",
                "description": f"{speed.description} updated updated",
            }
            response = self.client.put(url, data, format="json")
            self.assertEqual(response.status_code, 400)

    def test_speed_partial_update(self):
        for speed in self.testuserone.speed_set.all():
            url = reverse("speed-detail", kwargs={"pk": str(speed.id)})
            data = {
                "name": f"{speed.name} updated",
                "description": f"{speed.description} updated",
                "speed_type": "relative",
                "tags": ["three", "four", "nine"],
                "kmph": 4.0,
                "estimated": False,
                "is_public": False,
            }

            self.client.logout()
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            self.client.force_login(self.testusertwo)
            response = self.client.patch(url, data, format="json")
            if not speed.is_public:
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.data["detail"],
                    "Not found.",
                )
            else:
                self.assertEqual(response.status_code, 403)
                self.assertEqual(
                    response.data["detail"],
                    "You do not have permission to perform this action.",
                )

            self.client.force_login(self.testuserone)
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["name"], speed.name + " updated")
            self.assertEqual(
                response.data["description"], speed.description + " updated"
            )
            data = {
                "name": f"{speed.name} updated updated",
                "description": f"{speed.description} updated updated",
            }
            response = self.client.patch(url, data, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data["name"], speed.name + " updated updated"
            )
            self.assertEqual(
                response.data["description"],
                speed.description + " updated updated",
            )

    def test_speed_destroy(self):
        testuserone_speed_ids = []
        for speed in self.testuserone.speed_set.all():
            testuserone_speed_ids.append(speed.id)

            url = reverse("speed-detail", kwargs={"pk": str(speed.id)})

            self.client.logout()
            response = self.client.delete(url)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            self.client.force_login(self.testusertwo)
            response = self.client.delete(url)
            if not speed.is_public:
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.data["detail"],
                    "Not found.",
                )
            else:
                self.assertEqual(response.status_code, 403)
                self.assertEqual(
                    response.data["detail"],
                    "You do not have permission to perform this action.",
                )

            self.client.force_login(self.testuserone)
            response = self.client.delete(
                url,
                headers={
                    "Accept": "application/json",
                },
            )
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, None)

        counter = 0
        for speed in Speed.objects.filter(id__in=testuserone_speed_ids):
            self.assertEqual(speed.user.username, "deleted")
            counter += 1
        self.assertEqual(counter, len(testuserone_speed_ids))

        self.assertEqual(len(self.testuserone.speed_set.all()), 0)


class TestSpeedFeedback(CustomAPITestCase):
    def test_speed_feedback_list(self):
        url = reverse("speedfeedback-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        self.client.force_login(self.testusertwo)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for feedback in response.data["results"]:
            self.assertEqual(feedback["user"], self.testusertwo.username)
            if feedback["speed"]["user"] != self.testusertwo.username:
                self.assertEqual(feedback["speed"]["is_public"], True)

        self.client.force_login(self.testuserone)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for feedback in response.data["results"]:
            self.assertEqual(feedback["user"], self.testuserone.username)
            if feedback["speed"]["user"] != self.testuserone.username:
                self.assertEqual(feedback["speed"]["is_public"], True)

    def test_speed_feedback_retrieve(self):
        feedbacks = SpeedFeedback.objects.all()
        for feedback in feedbacks:
            url = reverse("speedfeedback-detail", kwargs={"pk": feedback.pk})

            self.client.logout()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            self.client.force_login(self.testusertwo)
            response = self.client.get(url)
            if feedback.user.username == self.testusertwo.username:
                self.assertEqual(response.status_code, 200)
                for key, val in response.data["speed"].items():
                    model_dict = model_to_dict(feedback.speed)
                    if key in model_dict and key != "user":
                        self.assertEqual(str(val), str(model_dict[key]))
            else:
                self.assertEqual(response.status_code, 403)
                self.assertEqual(
                    response.data["detail"],
                    "You do not have permission to perform this action.",
                )

    def test_speed_feedback_create(self):
        """
        Votes are only created in this view.
        This view does not utilize the create_or_update() method.
        """
        url = reverse("speedfeedback-list")

        # anon attempts to vote
        response = self.client.post(
            url,
            data={"speed": "d26c8bad-6548-4918-8e63-1bd59579917b", "vote": 1},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        self.client.force_login(self.testusertwo)

        # a client attemps to vote for the private `Speed` object
        response = self.client.post(
            url,
            data={"speed": "2dbc2429-a8cc-4f80-922a-5dbc4715a76c", "vote": 0},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

        # a client attempts to vote with incorrect `vote` value 0
        response = self.client.post(
            url,
            data={"speed": "66fca277-3329-49aa-96a2-cc240a659549", "vote": 0},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data[0],
            "You should either upvote or downvote, not vote with 0. Please use 1 or -1 instead.",
        )

        # a client votes correctly
        # ensures that the Speed object is updated correctly
        speed = Speed.objects.get(pk="66fca277-3329-49aa-96a2-cc240a659549")

        with transaction.atomic():
            response = self.client.post(
                url,
                data={
                    "speed": "66fca277-3329-49aa-96a2-cc240a659549",
                    "vote": 1,
                },
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data["speed"]["score"], speed.score + 1)

            speed_updated = Speed.objects.get(
                pk="66fca277-3329-49aa-96a2-cc240a659549"
            )
            self.assertEqual(speed_updated.upvotes, speed.upvotes + 1)

            transaction.set_rollback(True)

        response = self.client.post(
            url,
            data={"speed": "66fca277-3329-49aa-96a2-cc240a659549", "vote": -1},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["speed"]["score"], speed.score - 1)

        speed_updated = Speed.objects.get(
            pk="66fca277-3329-49aa-96a2-cc240a659549"
        )
        self.assertEqual(speed_updated.downvotes, speed.downvotes + 1)

        # a client attempts to vote second time for the same object
        response = self.client.post(
            url,
            data={"speed": "66fca277-3329-49aa-96a2-cc240a659549", "vote": 1},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data[0],
            "The UNIQUE constraint failed; the speed object has already been voted on.",
        )

        # a client attempts to vote on its own Speed object
        for speed in Speed.objects.filter(user=self.testusertwo):
            response = self.client.post(
                url,
                data={
                    "speed": f"{speed.pk}",
                    "vote": 1,
                },
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.data[0],
                "The UNIQUE constraint failed; the speed object has already been voted on.",
            )

    def test_speed_feedback_update(self):
        for speed_feedback in SpeedFeedback.objects.all():
            url = reverse(
                "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
            )

            # anon attempts to update a `SpeedFeedback` object
            self.client.logout()
            response = self.client.put(url, data={"vote": 1})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            # a client attempt to update 'SpeedFeedback' object
            self.client.force_login(self.testusertwo)
            response = self.client.put(url, data={"vote": 1})
            self.assertEqual(response.status_code, 405)
            self.assertEqual(
                response.data["detail"], 'Method "PUT" not allowed.'
            )

    def test_speed_feedback_partial_update(self):
        for speed_feedback in SpeedFeedback.objects.all():
            url = reverse(
                "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
            )

            # anon attempts to update a `SpeedFeedback` object
            self.client.logout()
            response = self.client.patch(url, data={"vote": 1})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "Authentication credentials were not provided.",
            )

            # a client attempt to update 'SpeedFeedback' object
            saved_score = speed_feedback.speed.score

            self.client.force_login(self.testusertwo)
            response = self.client.patch(url, data={"vote": 1})

            if speed_feedback.user != self.testusertwo:
                self.assertEqual(response.status_code, 403)
            else:
                if speed_feedback.vote != 1:
                    self.assertNotEqual(
                        response.data["speed"]["score"],
                        saved_score,
                    )
                self.assertEqual(response.status_code, 200)

            # a client attempt to update 'SpeedFeedback' object
            self.client.force_login(self.testuserone)
            response = self.client.patch(url, data={"vote": 1})

            if speed_feedback.user != self.testuserone:
                self.assertEqual(response.status_code, 403)
            else:
                self.assertEqual(response.status_code, 200)

    def test_speed_feedback_partial_update_of_downvote(self):
        # make sure that updates result in a correct score of 'Speed' objects
        # vote: downvote, user: testuserone, speed: "67e77deb-13d5-43fa-af9f-cc6f1b2a1c5c"
        speed_feedback = SpeedFeedback.objects.get(pk=8)
        speed_score = speed_feedback.speed.score
        speed_upvotes = speed_feedback.speed.upvotes
        speed_downvotes = speed_feedback.speed.downvotes

        url = reverse(
            "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
        )

        with transaction.atomic():
            self.client.force_login(self.testuserone)
            response = self.client.patch(
                url,
                data={
                    "speed": str(speed_feedback.speed.pk),
                    "vote": 1,
                    "user": str(self.testuserone.pk),
                },
            )
            self.assertEqual(response.data[0], "Can't change the speed field.")
            # user is set to read_only
            self.assertEqual(len(response.data), 1)

            response = self.client.patch(
                url,
                data={
                    "vote": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score + 2)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes + 1)
            self.assertEqual(curr_speed.downvotes, speed_downvotes - 1)

            self.client.logout()
            transaction.set_rollback(True)

        with transaction.atomic():
            self.client.force_login(self.testuserone)

            response = self.client.patch(
                url,
                data={
                    "vote": -1,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes)
            self.assertEqual(curr_speed.downvotes, speed_downvotes)

            self.client.logout()
            transaction.set_rollback(True)

        with transaction.atomic():
            self.client.force_login(self.testuserone)

            response = self.client.patch(
                url,
                data={
                    "vote": 0,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score + 1)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes)
            self.assertEqual(curr_speed.downvotes, speed_downvotes - 1)

            self.client.logout()
            transaction.set_rollback(True)

    def test_speed_feedback_partial_update_of_upvote(self):
        # make sure that updates result in a correct score of 'Speed' objects
        # vote: upvote, user: testuserone, speed: "d26c8bad-6548-4918-8e63-1bd59579917b"
        speed_feedback = SpeedFeedback.objects.get(pk=7)
        speed_score = speed_feedback.speed.score
        speed_upvotes = speed_feedback.speed.upvotes
        speed_downvotes = speed_feedback.speed.downvotes

        url = reverse(
            "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
        )

        with transaction.atomic():
            self.client.force_login(self.testuserone)
            response = self.client.patch(
                url,
                data={
                    "speed": str(speed_feedback.speed.pk),
                    "vote": 1,
                    "user": str(self.testuserone.pk),
                },
            )
            self.assertEqual(response.data[0], "Can't change the speed field.")
            # user is set to read_only
            self.assertEqual(len(response.data), 1)

            response = self.client.patch(
                url,
                data={
                    "vote": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes)
            self.assertEqual(curr_speed.downvotes, speed_downvotes)

            self.client.logout()
            transaction.set_rollback(True)

        with transaction.atomic():
            self.client.force_login(self.testuserone)

            response = self.client.patch(
                url,
                data={
                    "vote": -1,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score - 2)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes - 1)
            self.assertEqual(curr_speed.downvotes, speed_downvotes + 1)

            self.client.logout()
            transaction.set_rollback(True)

        with transaction.atomic():
            self.client.force_login(self.testuserone)

            response = self.client.patch(
                url,
                data={
                    "vote": 0,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["speed"]["score"], speed_score - 1)
            curr_speed = Speed.objects.get(pk=speed_feedback.speed.id)
            self.assertEqual(curr_speed.upvotes, speed_upvotes - 1)
            self.assertEqual(curr_speed.downvotes, speed_downvotes)

            self.client.logout()
            transaction.set_rollback(True)

    def test_speed_feedback_partial_update_data_reveal(self):
        """
        A user attempts to update its vote of the `Speed` object, added by a different
        user, that changed the `is_public` field to `False`.
        """

        # vote: upvote, user: testuserone, speed: "d26c8bad-6548-4918-8e63-1bd59579917b"
        speed_feedback = SpeedFeedback.objects.get(pk=7)
        speed = Speed.objects.get(pk="d26c8bad-6548-4918-8e63-1bd59579917b")
        speed.is_public = False
        speed.save()

        self.client.force_login(self.testuserone)

        url = reverse(
            "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
        )

        response = self.client.patch(
            url,
            data={
                "vote": -1,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_speed_feedback_destroy(self):
        # vote: upvote, user: testuserone, speed: "d26c8bad-6548-4918-8e63-1bd59579917b"
        speed_feedback = SpeedFeedback.objects.get(pk=7)

        url = reverse(
            "speedfeedback-detail", kwargs={"pk": str(speed_feedback.id)}
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "Authentication credentials were not provided.",
        )

        self.client.force_login(self.testuserone)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.data["detail"],
            'Method "DELETE" not allowed.',
        )
