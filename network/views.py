from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Follow, Post, User
from .forms import AddPostForm


def index(request):
    all_posts = Post.objects.all().order_by("-created_at")

    if request.method == "POST":
        form = AddPostForm(request.POST)

        if form.is_valid():
            Post.objects.create(body=form.cleaned_data["body"], user=request.user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/index.html",
                context={
                    "form": form,
                    "all_posts": all_posts,
                    "title": "All Posts",
                    "errors": form.errors,
                    "index": True,
                },
            )
    else:
        form = AddPostForm()
        return render(
            request,
            "network/index.html",
            context={
                "form": form,
                "all_posts": all_posts,
                "title": "All Posts",
                "index": True,
            },
        )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def profile(request, username):
    # The user we are reaching for
    profile_owner = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_owner).order_by("-created_at")
    request_user = User.objects.get(pk=request.user.id)

    # Check if the user is viewing their own profile
    viewer_is_owner = request_user.id == profile_owner.id

    is_followed = Follow.objects.filter(
        follower=request_user, followed=profile_owner
    ).exists()

    return render(
        request,
        "network/profile.html",
        context={
            "profile_owner": profile_owner,
            "posts": posts,
            "viewer_is_owner": viewer_is_owner,
            "is_followed": is_followed,
        },
    )


@login_required
def follow_unfollow(request, username, action: str):
    if request.method == "POST":
        profile = get_object_or_404(User, username=username)
        if action.upper() == "FOLLOW":
            Follow.objects.get_or_create(follower=request.user, followed=profile)
        elif action.upper() == "UNFOLLOW":
            follow_instance = Follow.objects.filter(
                follower=request.user, followed=profile
            )
            if follow_instance:
                follow_instance.delete()

        return HttpResponseRedirect(reverse("profile", args=[username]))


@login_required
def following_feed(request):
    user = get_object_or_404(User, pk=request.user.id)
    following_user_ids = user.following.values_list("followed_id", flat=True)

    posts = Post.objects.filter(user__id__in=following_user_ids)

    return render(
        request,
        "network/index.html",
        context={"title": "following", "all_posts": posts, "index": False},
    )
    
