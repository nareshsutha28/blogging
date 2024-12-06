from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    slug = models.SlugField(unique=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    '''I have desided scenario from my side that multiple blog post can have same title,
    If any will come like that i will add that timestamp to make slug unique.'''  
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        try:
            super(Post, self).save(*args, **kwargs)
        except Exception as e: 
            self.slug = slugify(self.slug+str(self.timestamp)[:19])
            super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"
