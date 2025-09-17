# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    
    # URLs AJAX
    path("ajax/post/<int:pk>/", views.get_post_data_ajax, name="get_post_data_ajax"),
    path("ajax/add-comment/", views.add_comment_ajax, name="add_comment_ajax"),
    path("ajax/like-post/", views.like_post_ajax, name="like_post_ajax"),
    path("ajax/search/", views.search_posts_ajax, name="search_posts_ajax"),
]