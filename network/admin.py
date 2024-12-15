from django.contrib import admin
from .models import User, Post, Follow, Like


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "is_active", "date_joined"]
    search_fields = ["username"]
    list_per_page = 10


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["user", "short_body", "created_at"]
    search_fields = ["username__istartswith", "short_body__istartswith"]
    autocomplete_fields = ["user"]
    list_per_page = 10

    def short_body(self, post):
        return post.body[:30] + "..."


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "followed"]
    search_fields = ["follower__user", "following__user"]
    autocomplete_fields = ["follower", "followed"]
    list_per_page = 10


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["user", "post", "created_at"]
    autocomplete_fields = ["post", "user"]
    list_per_page = 10
