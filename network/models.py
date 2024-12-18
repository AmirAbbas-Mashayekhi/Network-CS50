from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Follow(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow_relationship"
            )
        ]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["followed"]),
        ]

    def __str__(self):
        return f"{self.follower} follows {self.followed}"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.body[:30]}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_like_relationship"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"
