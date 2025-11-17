
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("new_post/", views.new_post, name="new_post"),
    path("post/<int:post_id>", views.posts, name="post"),
    path("like/<slug:target>", views.likes, name="like"),
    path("comment/<int:post_id>", views.comments, name="comment"),
    path("comment/<int:post_id>/modal", views.load_comment_modal, name="load_comment_modal"),
    path("profile/<int:user_id>", views.profile_page, name="profile"),
    path("view_post/<int:post_id>", views.view_post, name="view_post"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("following/", views.following_page, name="following"),
    path("edit/<int:post_id>", views.edit_post, name="edit_post"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)