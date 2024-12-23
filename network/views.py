from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Exists, OuterRef, Value, BooleanField
from django.db.models.functions import Coalesce


from .models import Follow, Like, Post, User
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

    # Fetch posts and annotate with like status
    posts = Post.objects.annotate(
        like_count=Coalesce(Count("likes"), Value(0))
    ).order_by("-created_at")

    if request.user.is_authenticated:
        user_likes = Like.objects.filter(user=request.user, post=OuterRef("pk"))
        posts = posts.annotate(liked_by_user=Exists(user_likes))
    else:
        posts = posts.annotate(liked_by_user=Value(False, output_field=BooleanField()))

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


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).annotate(
        like_count=Coalesce(Count('likes'), Value(0))
    ).order_by("-created_at")

    if request.user.is_authenticated:
        user_likes = Like.objects.filter(user=request.user, post=OuterRef('pk'))
        posts = posts.annotate(
            liked_by_user=Exists(user_likes)
        )
    else:
        posts = posts.annotate(
            liked_by_user=Value(False, output_field=BooleanField())
        )

    # Pagination
    paginator = Paginator(posts, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "network/profile.html",
        context={
            "profile_owner": user,
            "page_obj": page_obj,
            "title": f"{user.username}'s Profile",
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

    posts = Post.objects.filter(user__id__in=following_user_ids).order_by("-created_at")

    # Pagination
    pagination = Paginator(posts, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = pagination.get_page(page_number)

    return render(
        request,
        "network/index.html",
        context={"title": "following", "page_obj": page_obj, "index": False},
    )


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    # Get the post or return a 404 if it doesn't exist
    post = get_object_or_404(Post, pk=post_id)

    # Check if the user owns the post
    if post.user != request.user:
        return JsonResponse({"error": "Access Denied"}, status=403)

    # Extract and validate the updated body from request.POST
    new_body = request.POST.get("body")
    if not new_body:
        return JsonResponse({"error": "Post body is required."}, status=400)

    # Update the post
    post.body = new_body
    post.save()

    return JsonResponse({"message": "Post updated successfully."}, status=200)


@login_required
@csrf_exempt
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    post = get_object_or_404(Post, pk=post_id)
    user = request.user

    # Check if the user has already liked the post
    liked = Like.objects.filter(user=user, post=post).exists()

    if liked:
        # Unlike the post
        Like.objects.filter(user=user, post=post).delete()
        liked = False
    else:
        # Like the post
        Like.objects.create(user=user, post=post)
        liked = True

    # Return the new like count
    like_count = post.likes.count()
    return JsonResponse({"liked": liked, "like_count": like_count}, status=200)
