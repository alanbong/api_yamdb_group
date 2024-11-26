from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

# from reviews.views import (
#     CategoryViewSet,
#     GenreViewSet,
#     TitleViewSet,
#     CommentViewSet,
#     ReviewViewSet,
#     UserViewSet,
#     SignUpView,
# )

# v1_router = DefaultRouter()
# v1_router.register('categories', CategoryViewSet, basename='category')
# v1_router.register('genres', GenreViewSet, basename='genre')
# v1_router.register('titles', TitleViewSet, basename='title')
# v1_router.register('users', UserViewSet, basename='user')

# v1_router.register(r'titles/(?P<title_id>\d+)/reviews',
#                    ReviewViewSet, basename='title-reviews')

# v1_router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='title-comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/auth/signup/', SignUpView.as_view()),
    # path('api/v1/', include(v1_router.urls)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
