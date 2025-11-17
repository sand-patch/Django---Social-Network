from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Posts, Likes, Comments, Followers
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse


def index(request):
    posts = Posts.objects.order_by("-created").all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 

    return render(request, "network/index.html", {
        "request_user": request.user.id,
        "page_obj" : page_obj,
        "MEDIA_URL" : settings.MEDIA_URL
        })


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required    
def new_post(request):
    try:
        profile_user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

    if (request.method == 'POST'):
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if (not title and not content):
            return render(request, 'network/new_post.html', {
                "ERROR" : "You must provide a title or text content."
            })
        if (len(title) > 120):
            return render(request, 'network/new_post.html', {
                "ERROR" : "Title is too long. Max 120 characters."
            })
        if (image):
            if (image.content_type not in ['image/jpeg', 'image/png', 'image/gif']):
                return render(request, 'network/new_post.html', {
                    "ERROR" : "Only JPEG, PNG, and GIF images are allowed."
                })
            if (image.size > (5 * 1024 * 1024)):
                return render(request, 'network/new_post.html', {
                    "ERROR" : "Image file is too large (max 5MB)."
                })
        Posts.objects.create(
            author=request.user,
            title=title,
            body=content,
            image=image
        )

        profile_user.posts_cnt += 1
        profile_user.save()
        return HttpResponseRedirect(reverse("index"))


    return render(request, "network/new_post.html")

@login_required
def posts(request, post_id):
    try:
        post = Posts.objects.get(pk=post_id)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not Found."}, status=404)
    
    if (request.method == "GET"):
        return JsonResponse(post.serialize())
    elif (request.method == "PUT"):
        existing_like = Likes.objects.filter(user=request.user, post=post)
        if (not existing_like):
            Likes.objects.create(
                user=request.user,
                post=post
            )
            post.likes += 1
            post.save()
            data = {}
            data[post.id] = post.likes
        return JsonResponse(data, status=200)
    elif (request.method == "DELETE"):
        try:
            Likes.objects.filter(post=post, user=request.user).delete()
            post.likes = max(0, post.likes - 1)
            post.save()
            data = {}
            data[post.id] = post.likes
            return JsonResponse(data, status=200)
        except Likes.DoesNotExist:
            return JsonResponse({"error": "Like not Found"}, status=404)
    else:
        return JsonResponse({
            "error" : " GET, PUT or DELETE request required"
        }, status=400)

@login_required
def likes(request, target):
    if target == "all":
        likes_qs = Likes.objects.filter(user=request.user)
        data = {}
        for like in likes_qs:
            data[like.post.id] = like.post.likes  
        return JsonResponse(data, status=200)

    else:
        try:
            post = Posts.objects.get(pk=target)
        except Posts.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        liked = Likes.objects.filter(post=post, user=request.user).exists()
        data = {}
        if liked:
            data[post.id] = post.likes
        return JsonResponse(data, status=200)
    
def get_post_comments(post_id):
    post = Posts.objects.get(id=post_id)
    comments = Comments.objects.filter(post=post).order_by("-commented_at")
    return {
            "post": post.id,
            "total_comments": comments.count(),
            "comments": [
                {
                    "user": {
                        "id": comment.user.id,
                        "username": comment.user.username
                    },
                    "body": comment.body,
                    "commented_at": comment.commented_at.strftime("%Y-%m-%d%H:%M:%S")
                }
                for comment in comments
            ]
        }

@login_required
def comments(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    if (request.method == "POST"):
        data = json.loads(request.body)

        if (data.get("comment") is not None):
            Comments.objects.create(
                user=request.user,
                post=post,
                body=data["comment"]
            )
            return HttpResponse(status=204)
        else:
            return JsonResponse({"error": "Comment Failed"}, status=404)
    elif (request.method == "GET"):
        try:
            data = get_post_comments(post_id)
        except Posts.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        return JsonResponse(data, status=200)
    
    return JsonResponse({"error": "Bad Request"}, status=400)

def load_comment_modal(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    
    data = get_post_comments(post_id)

    if (data):
        return render(request, "network/components/comment_modal.html", {
            "post": post,
            "total_comments": data["total_comments"],
            "comments": data["comments"]
        })
    return JsonResponse({"error": "Bad Request"}, status=400)

def profile_page(request, user_id):
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, "network/profile.html", {
            "ERROR": True
        })
    
    posts = Posts.objects.filter(author=profile_user).order_by("-created")
    
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "post_count": profile_user.posts_cnt,
        "follower_count": profile_user.followers_cnt,
        "following_count": profile_user.following_cnt,
        "posts": posts,
        "MEDIA_URL" : settings.MEDIA_URL
    })

def view_post(request, post_id):
    if (request.method == "GET"):
        try:
            post = Posts.objects.get(id=post_id)
        except Posts.DoesNotExist:
            return render(request, "network/view_post.html", {
                "ERROR": True
            })
        return render(request, "network/view_post.html", {
            "request_user": request.user.id,
            "post" : post,
            "MEDIA_URL": settings.MEDIA_URL
        })

@login_required
def follow(request, user_id):
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)

    if (request.method == "PUT"):
        follwer = Followers.objects.filter(following=user_id, follower=request.user).exists()   
        if (not follwer):
            Followers.objects.create(
                follower=request.user,
                following=profile_user
            )
            profile_user.followers_cnt += 1
            profile_user.save()
            request.user.following_cnt += 1
            request.user.save()
            data = {"followerCnt": profile_user.followers_cnt}
            return JsonResponse(data,status=200)
        else:
            return JsonResponse({"error": "User already follows this user"}, status=409)
    elif (request.method == "DELETE"):
        try:
            Followers.objects.filter(following=user_id, follower=request.user).delete()
            profile_user.followers_cnt = max(0, profile_user.followers_cnt - 1)
            profile_user.save()
            request.user.following_cnt = max(0, request.user.following_cnt - 1)
            request.user.save()
            data = {"followerCnt": profile_user.followers_cnt}
            return JsonResponse(data,status=200)
        except Followers.DoesNotExist:
            return JsonResponse({"error": "User not Found"}, status=404)
    elif (request.method == "GET"):
        follwer = Followers.objects.filter(following=user_id, follower=request.user).exists()
        return JsonResponse({
                "isFollower": follwer
        }, status=200)
    return JsonResponse({"error": "Bad Request"}, status=400)

def following_page(request):
    try:
        follow_users = Followers.objects.filter(follower=request.user).values_list("following", flat=True)
        posts = Posts.objects.filter(author__in=follow_users).order_by("-created")
    except Followers.DoesNotExist:
        return JsonResponse({"error": "Users not Found"}, status=404)
    
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 

    return render(request, "network/following.html", {
        "page_obj" : page_obj,
        "MEDIA_URL" : settings.MEDIA_URL
        })

def edit_post(request, post_id):
    try:
        post = Posts.objects.get(id=post_id)
    except Posts.DoesNotExist:
        return JsonResponse({"error": "Post not Found"}, status=404)
    if (post.author != request.user):
        return HttpResponseForbidden("You cannot edit another user's post.")
    
    if (request.method == "PUT"):
        data = json.loads(request.body)
        title = data.get("title")
        body = data.get("body")
        post.title = title
        post.body = body
        post.save()
        return JsonResponse({
            "success": True, 
            "body": post.body,
            "title": post.title
            }, status=200)
        