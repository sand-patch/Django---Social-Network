from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers_cnt = models.IntegerField(default=0)
    following_cnt = models.IntegerField(default=0)
    posts_cnt = models.IntegerField(default=0)

class Posts(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    body = models.TextField()
    likes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "title": self.title,
            "body": self.body,
            "likes": self.likes,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
        }

class Likes(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, related_name='likes_objs')
    liked_at = models.DateTimeField(auto_now_add=True)
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "post_id": self.post.id,
        }
    def likeState(self):
        return {
            "post_id" : self.post.id,
            "liked": True,
            "like_count": self.post.likes
        }


class Comments(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
    def serialize(self):
        return {
            "user": self.user,
            "post": self.post,
            "body": self.body,
            "commented_at": self.commented_at
        }

class Followers(models.Model):
    follower = models.ForeignKey('User', on_delete=models.CASCADE)
    following = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='following_objs')
    timestamp = models.DateTimeField(auto_now_add=True)