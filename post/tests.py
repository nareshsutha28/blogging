import unittest
from django.test import Client
from rest_framework import status
from django.contrib.auth import get_user_model
from post.models import Post, Comment
import json

User = get_user_model()

class PostCreationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'testuser@gmail.com'
        self.password = 'testpassword'
        # Create a test user
        self.user = User.objects.create_user(email=self.email)
        self.user.set_password(self.password)
        self.user.save()        

        self.login_url = '/login/'  # Update with your actual login endpoint
        self.post_create_url = '/posts/'  # Update with your actual post creation endpoint
        
        # Authenticate and get JWT token
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        }, content_type='application/json')
        self.token = json.loads(response.content)["data"].get('access')
        
    def test_create_post_success(self):
        # Prepare valid post data
        post_data = {
            'title': 'Test Post',
            'body': 'This is a test post.',
        }

        # Send POST request to create a post
        response = self.client.post(self.post_create_url, post_data, 
                                     HTTP_AUTHORIZATION=f'Bearer {self.token}', 
                                     content_type='application/json')

        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the post is created correctly
        response_data = json.loads(response.content)
        self.assertEqual(response_data['data']['title'], post_data['title'])
        self.assertEqual(response_data['data']['body'], post_data['body'])
        self.assertEqual(response_data['data']['author'], self.user.email)

    def test_create_post_unauthenticated(self):
        # Try to create post without authentication
        post_data = {
            'title': 'Test Post Without Auth',
            'body': 'This post should not be created without authentication.',
        }

        response = self.client.post(self.post_create_url, post_data, content_type='application/json')

        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_post_invalid_data(self):
        # Send invalid data (e.g., too short title)
        post_data = {
            'title': 'T',  # Invalid title (too short)
            'body': 'This is an invalid post with a short title.',
        }

        response = self.client.post(self.post_create_url, post_data,
                                     HTTP_AUTHORIZATION=f'Bearer {self.token}',
                                     content_type='application/json')

        print("sfddgds", response.data)
        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that title validation error is in the response
        response_data = json.loads(response.content)
        self.assertIn('title', response_data["data"])

    def tearDown(self):
        # Clean up after tests
        User.objects.all().delete()
        Post.objects.all().delete()


class TopCommentedPostsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'testuser@gmail.com'
        self.password = 'testpassword'
        # Create a test user
        self.user = User.objects.create_user(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.login_url = '/login/'  # Update with your actual login endpoint
        self.top_commented_posts_url = '/top-five-posts/'  # Update with your actual top commented posts endpoint
        
        # Authenticate and get JWT token
        response = self.client.post(self.login_url, {
            'email': self.email,
            'password': self.password
        }, content_type='application/json')
        self.token = json.loads(response.content)["data"].get('access')

        # Create test posts and comments
        self.create_test_posts_and_comments()

    def create_test_posts_and_comments(self):
        # Create 5 posts with different comment counts
        for i in range(5):
            post = Post.objects.create(title=f'Post {i + 1}', body='This is a test post.', author=self.user)
            # Create different numbers of comments for each post
            for j in range(i + 1):  # Number of comments increases for each post
                Comment.objects.create(post=post, author=self.user, body=f'Comment {j + 1} for post {i + 1}')

    def test_top_commented_posts_success(self):
        # Send GET request to retrieve the top 5 most commented posts
        response = self.client.get(self.top_commented_posts_url, 
                                   HTTP_AUTHORIZATION=f'Bearer {self.token}', 
                                   content_type='application/json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains data for top 5 posts
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['data']), 5)

        # Ensure the posts are ordered by comment count and timestamp
        post_data = response_data['data']
        previous_comment_count = post_data[0]['comment_count']
        previous_timestamp = post_data[0]['timestamp']
        for post in post_data:
            self.assertGreaterEqual(previous_comment_count, post['comment_count'])
            # If the comment count is the same, check if the posts are ordered by timestamp
            if previous_comment_count == post['comment_count']:
                self.assertGreaterEqual(previous_timestamp, post['timestamp'])
            previous_comment_count = post['comment_count']
            previous_timestamp = post['timestamp']

    def test_top_commented_posts_unauthenticated(self):
        # Send GET request to retrieve top 5 posts without authentication (missing token)
        response = self.client.get(self.top_commented_posts_url, content_type='application/json')

        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_top_commented_posts_no_posts(self):
        # Delete all posts to test scenario where there are no posts in the database
        Post.objects.all().delete()

        # Send GET request to retrieve top 5 posts
        response = self.client.get(self.top_commented_posts_url, 
                                   HTTP_AUTHORIZATION=f'Bearer {self.token}', 
                                   content_type='application/json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains no data (empty list)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['data']), 0)

    def tearDown(self):
        # Clean up after tests
        User.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()
