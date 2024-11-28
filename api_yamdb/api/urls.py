from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    CommentViewSet,
    ReviewViewSet,
    SignupView,
    TokenView,
    CustomUserViewSet,
    UserMeViewSet
)

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('titles', TitleViewSet, basename='title')
# v1_router.register('users/me', UserMeViewSet, basename='users-me')
v1_router.register('users', CustomUserViewSet, basename='users')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='title-reviews')

v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='title-comments')

urlpatterns = [
    path('users/me/', UserMeViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='users-me'),
    path('', include(v1_router.urls)),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
]
