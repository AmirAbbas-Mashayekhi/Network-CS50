from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Follow, Post, User
from .forms import AddPostForm


def index(request):
    # Handle form submission
    errors = {}
    if request.method == "POST":
        form = AddPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("index")
        else:
            errors = form.errors

    # Fetch posts and paginate
    posts = Post.objects.all().order_by("-created_at")

    # Pagination
    paginator = Paginator(posts, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "network/index.html",
        context={
            "form": AddPostForm(),
            "page_obj": page_obj,
            "errors": errors,
            "index": True,
            "title": "Home",
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
            return redirect(reverse("index"))
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
    return redirect(reverse("index"))


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
        return redirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def profile(request, username):
    # Get the user whose profile is being viewed
    profile_owner = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_owner).order_by("-created_at")
    request_user = request.user

    # Pagination
    paginator = Paginator(posts, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Determine if the current user owns the profile
    viewer_is_owner = request_user == profile_owner

    # Check if the current user is following the profile owner
    is_followed = Follow.objects.filter(
        follower=request_user, followed=profile_owner
    ).exists()

    return render(
        request,
        "network/profile.html",
        context={
            "profile_owner": profile_owner,
            "page_obj": page_obj,
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

        return redirect(reverse("profile", args=[username]))


@login_required
def following_feed(request):
    user = get_object_or_404(User, pk=request.user.id)
    following_user_ids = user.following.values_list("followed_id", flat=True)

    posts = Post.objects.filter(user__id__in=following_user_ids).order_by('-created_at')

    # Pagination
    pagination = Paginator(posts, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = pagination.get_page(page_number)

    return render(
        request,
        "network/index.html",
        context={"title": "following", "page_obj": page_obj, "index": False},
    )
