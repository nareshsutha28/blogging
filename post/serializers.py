from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    slug = serializers.ReadOnlyField()  # Make slug read-only

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'author', 'timestamp', 'slug']
