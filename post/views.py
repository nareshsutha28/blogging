from rest_framework.generics import GenericAPIView
from django.db.models import Q, Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from post.models import Post
from post.serializers import (PostSerializer, CommentSerializer,
                            TopCommentPostSerializer)
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


class CommentListCreateAPIView(GenericAPIView):
    """
    API view to list and create comments for a specific post identified by its slug.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination  # Enable pagination

    def get_post_object(self, slug):
        """
        Get a Post object by its slug. Returns None if not found.
        """
        return Post.objects.filter(slug=slug).first()

    @swagger_auto_schema(
        operation_description="Get the list of comments for a post with pagination ordered by timestamp",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response("Paginated list of comments", CommentSerializer(many=True)),
            400: openapi.Response(description="Invalid slug", examples={
                "application/json": {"status": 400, "msg": "Invalid slug", "data": []}
            }),
        },
    )
    def get(self, request, slug):
        """
        Handle GET requests to fetch a paginated list of comments for a post.
        """
        post_object = self.get_post_object(slug)
        if not post_object:
            return get_response(status.HTTP_400_BAD_REQUEST, "Invalid slug data", [])

        comment_queryset = post_object.comments.select_related("post", "author").all().order_by("-timestamp")

        # Paginate the queryset
        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(comment_queryset, request)
        serializer = CommentSerializer(paginated_comments, many=True)

        return paginator.get_paginated_response({
            "status": status.HTTP_200_OK,
            "msg": "Retrieved comments successfully",
            "data": serializer.data
        })

    @swagger_auto_schema(
        operation_description="Create a new comment for a post",
        request_body=CommentSerializer,
        responses={
            201: openapi.Response(description="Comment created successfully", examples={
                "application/json": {"status": 201, "msg": "Comment created successfully", "data": {}}
            }),
            400: openapi.Response(description="Invalid Request Body", examples={
                "application/json": {"status": 400, "msg": "Invalid Request Body", "data": {}}
            }),
        },
    )
    def post(self, request, slug):
        """
        Handle POST requests to create a comment for a specific post.
        """
        post_object = self.get_post_object(slug)
        if not post_object:
            return get_response(status.HTTP_400_BAD_REQUEST, "Invalid slug data", [])

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post_object)
            return get_response(status.HTTP_201_CREATED, "Comment created successfully", serializer.data)

        return get_response(status.HTTP_400_BAD_REQUEST, "Invalid Request Body", serializer.errors)


class TopCommentedPostsAPIView(GenericAPIView):
    """
    API to get the top five most commented posts.
    """
    permission_classes = [IsAuthenticated]  # Anyone can access this API

    @swagger_auto_schema(
        operation_description="Retrieve the top five most commented posts",
        responses={
            200: openapi.Response(description="Posts fetching Successfully", examples={
                "application/json": {"status": 200, "msg": "Posts fetching Successfully", "data": []}
            })},
    )
    def get(self, request):
        # Annotate posts with the count of their comments and order them by count (descending)
        top_commented_posts = Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count', '-timestamp')
        if top_commented_posts.count() > 5:
            top_commented_posts = top_commented_posts[:5]
        
        serializer = TopCommentPostSerializer(top_commented_posts, many=True)
        return get_response(status.HTTP_200_OK, "Top commented posts retrieved successfully", serializer.data)