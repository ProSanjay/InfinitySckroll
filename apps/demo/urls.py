from django.urls import path
from .views import post_list_view, register_user, create_post_view, login_view, add_comment_view

urlpatterns = [
    path('api/posts/', post_list_view, name='post-list'),
    path('register/', register_user, name='register'),
    path('api/posts/create/', create_post_view, name='post-create'),
    path('api/login/', login_view, name='login'),
    path('api/comments/add/', add_comment_view, name='comment-add'),
]
