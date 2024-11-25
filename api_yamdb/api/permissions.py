from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class OwnerOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, post):
        return (request.method in permissions.SAFE_METHODS
                or post.author == request.user)
