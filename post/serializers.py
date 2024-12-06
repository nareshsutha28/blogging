from rest_framework import serializers
from post.models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    slug = serializers.ReadOnlyField()  # Make slug read-only

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'timestamp', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    post = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'post', 'timestamp']
