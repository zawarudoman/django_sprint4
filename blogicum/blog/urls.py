from django.urls import path

from . import views

app_name = 'blog'


urlpatterns = [
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>',
        views.CommentUpdateViews.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteViews.as_view(),
        name='delete_comment'
    ),
    path('', views.IndexView.as_view(), name='index'),
    path(
        'profile/edit/',
        views.ProfileUpdateViews.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.ProfileListViews.as_view(),
        name='profile'
    ),
    path(
        'posts/create/',
        views.PostCreateViews.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailViews.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateViews.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteViews.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/comment',
        views.CommentCreateViews.as_view(),
        name='add_comment'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'),
]
