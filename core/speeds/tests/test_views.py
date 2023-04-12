# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from ..models import Speed
# from ..serializers import SpeedSerializer
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class SpeedTests(APITestCase):
    
#     @classmethod
#     def setUpTestData(cls) -> None:
#         pass


#     def setUp(self):
#         self.author = User.objects.create_user(
#             username='test_author', email='author@example.com', password='password')
#         self.data = {
#             "name": "Test Speed",
#             "description": "Test Speed Description",
#             "tags": "test, speed, drf",
#             "kmph": 100,
#             "author": self.author.id,
#             "public": True
#         }
#         self.serializer = SpeedSerializer(data=self.data)

#     def test_create_speed(self):
#         self.client.force_login(self.author)
#         response = self.client.post(reverse('speed-list'), self.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Speed.objects.count(), 1)
#         self.assertEqual(Speed.objects.get().name, self.data['name'])

#     def test_update_speed_detail(self):
#         data = {
#             "name": "New Name",
#             "description": "New Description",
#             "tags": "new, tags, drf",
#             "kmph": 150,
#             "public": False
#         }
#         self.client.force_login(self.author)
#         response = self.client.put(self.url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.speed.refresh_from_db()
#         self.assertEqual(self.speed.name, data["name"])
#         self.assertEqual(self.speed.description, data["description"])
#         self.assertEqual(self.speed.tags, data["tags"])
#         self.assertEqual(self.speed.kmph, data["kmph"])
#         self.assertEqual(self.speed.public, data["public"])