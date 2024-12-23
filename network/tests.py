from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Like, Follow

User = get_user_model()


class NetworkTestCase(TestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

        # Create posts
        self.post1 = Post.objects.create(user=self.user1, body="Post by user1")
        self.post2 = Post.objects.create(user=self.user2, body="Post by user2")

        # Create client
        self.client = Client()

    def test_user_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword",
                "confirmation": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        response = self.client.post(
            reverse("login"), {"username": "user1", "password": "password1"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_create_post(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("index"), {"body": "New post by user1"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(body="New post by user1").exists())

    def test_like_post(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse("toggle-like", args=[self.post2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.user1, post=self.post2).exists())

    def test_unlike_post(self):
        self.client.login(username="user1", password="password1")
        Like.objects.create(user=self.user1, post=self.post2)
        response = self.client.post(reverse("toggle-like", args=[self.post2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(user=self.user1, post=self.post2).exists())

    def test_follow_user(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(
            reverse("follow_unfollow", args=[self.user2.username, "FOLLOW"])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_unfollow_user(self):
        self.client.login(username="user1", password="password1")
        Follow.objects.create(follower=self.user1, followed=self.user2)
        response = self.client.post(
            reverse("follow_unfollow", args=[self.user2.username, "UNFOLLOW"])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(follower=self.user1, followed=self.user2).exists()
        )

    def test_profile_view(self):
        response = self.client.get(reverse("profile", args=[self.user1.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post1.body)
        self.assertContains(response, self.post2.body)

    def test_following_feed_view(self):
        self.client.login(username="user1", password="password1")
        Follow.objects.create(follower=self.user1, followed=self.user2)
        response = self.client.get(reverse("following_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post2.body)
        self.assertNotContains(response, self.post1.body)
