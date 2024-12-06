from rest_framework import serializers
from post.models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    slug = serializers.ReadOnlyField()  # Make slug read-only

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'timestamp', 'slug']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Title cannot exceed 100 characters.")
        return value

    def validate_body(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Body must be at least 5 characters long.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    post = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'post', 'timestamp']

    def validate_body(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value


class TopCommentPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    post = serializers.ReadOnlyField(source='post.title')
    comment_count = serializers.CharField() 

    class Meta:
        model = Comment
        fields = ['id', 'body', 'author', 'post', 'comment_count', 'timestamp']
