from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profiles/<str:username>", views.profile, name="profile"),
    path(
        "profiles/<str:username>/<str:action>/",
        views.follow_unfollow,
        name="follow_unfollow",
    ),
    path("following/", views.following_feed, name="following_feed"),
    path("edit/<int:post_id>", views.edit_post, name="edit-post"),
]
