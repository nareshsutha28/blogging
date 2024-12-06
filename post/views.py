from rest_framework.generics import GenericAPIView
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from post.models import Post
from post.serializers import PostSerializer
from blogging.utils import get_response


class PostListCreateAPIView(GenericAPIView):
    """
    List all posts with pagination, and create a new post.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination  # Enable pagination for this view

    @swagger_auto_schema(
        operation_description="Get the list of posts with pagination",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('author', openapi.IN_QUERY, description="Filter posts by author (Firstname, Lastname or email)", type=openapi.TYPE_STRING),
            ],
        responses={200: openapi.Response("Paginated list of posts", PostSerializer(many=True))},
    )
    def get(self, request):
        print(dir(request),)
        authot_filter = request.query_params.get("author")
        # List order by timestamps
        post_queryset = Post.objects.all().order_by('-timestamp') 
        if authot_filter:
            post_queryset = post_queryset.filter(
                Q(author__first_name__icontains=authot_filter) |
                Q(author__last_name__icontains=authot_filter) |
                Q(author__email__icontains=authot_filter)
            )

        posts = self.paginate_queryset(post_queryset)
        serializer = PostSerializer(posts, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=PostSerializer,
        responses={
            201: openapi.Response(description="Post created successfully", examples={"application/json": {"status": 201, "msg": "Post created successfully", "data": {}}}),
            400: openapi.Response(description="Invalid Request Body", examples={"application/json": {"status": 400, "msg": "Invalid Request Body", "data": {}}}),
        },
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return get_response(status.HTTP_201_CREATED, "Post created successfully", serializer.data)
        return get_response(status.HTTP_400_BAD_REQUEST, "Invalid data", serializer.errors)


class PostDetailAPIView(GenericAPIView):
    """
    Retrieve, update, and delete posts by slug.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, slug):
        return Post.objects.filter(slug=slug).first()

    @swagger_auto_schema(
        operation_description="Retrieve a specific post by slug",
        responses={200: openapi.Response("Post fetched successfully", PostSerializer)},
    )
    def get(self, request, slug):
        post = self.get_object(slug)
        if post:
            serializer = PostSerializer(post)
            return get_response(status.HTTP_200_OK, "Post fetched successfully", serializer.data)
        return get_response(status.HTTP_404_NOT_FOUND, "Post not found", {})

    @swagger_auto_schema(
        operation_description="Update a post",
        request_body=PostSerializer,
        responses={
            200: openapi.Response(description="Post updated successfully", examples={"application/json": {"status": 200, "msg": "Post Updated successfully", "data": {}}}),
            400: openapi.Response(description="Post update failed", examples={"application/json": {"status": 400, "msg": "Post Not Updated", "data": {}}}),
        },
    )
    def put(self, request, slug):
        post = self.get_object(slug)
        if not post:
            return get_response(status.HTTP_404_NOT_FOUND, "Post not found", {})

        # Ensure the user is the author of the post
        if post.author != request.user:
            return get_response(status.HTTP_403_FORBIDDEN, "You are not authorized to update this post", {})

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return get_response(status.HTTP_200_OK, "Post updated successfully", serializer.data)

        return get_response(status.HTTP_400_BAD_REQUEST, "Invalid data", serializer.errors)

    def delete(self, request, slug):
        post = self.get_object(slug)
        if not post:
            return get_response(status.HTTP_404_NOT_FOUND, "Post not found", {})

        # Ensure the user is the author of the post
        if post.author != request.user:
            return get_response(status.HTTP_403_FORBIDDEN, "You are not authorized to delete this post", {})

        post.delete()
        return get_response(status.HTTP_200_OK, "Post deleted successfully", {})
