from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import Post, Comment  # Assumes these exist
from django.contrib.auth.models import User  # Assumes User model
from rest_framework.decorators import api_view

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
# from .serializers import UserSerializer

from django.contrib.auth import authenticate

class PostListPagination(PageNumberPagination):
    page_size = 10  # Adjust as needed

class PostCommentSerializer:
    """
    Serializes a Comment for API output.
    """
    def __init__(self, comment):
        self.comment = comment

    def data(self):
        return {
            "text": self.comment.text,
            "timestamp": self.comment.timestamp,
            "author": self.comment.user.username
        }

class PostSerializer:
    """
    Serializes a Post for API output, including up to 3 latest Comments.
    """
    def __init__(self, post):
        self.post = post

    def data(self):
        comments_qs = Comment.objects.filter(post=self.post).order_by('-timestamp')[:3]
        comments = [PostCommentSerializer(c).data() for c in comments_qs]
        return {
            "id": self.post.id,
            "text": self.post.text,
            "timestamp": self.post.timestamp,
            "author": self.post.user.username,
            "comment_count": Comment.objects.filter(post=self.post).count(),
            "comments": comments
        }

@api_view(['GET'])
def post_list_view(request):
    """
    GET /api/posts/
    Returns a paginated list of Posts ordered by latest timestamp.
    Each Post includes:
      - text
      - timestamp
      - author's username
      - comment count
      - up to 3 latest Comments (each with text, timestamp, author's username)

    Example response:
    {
      "count": 100,
      "next": "...",
      "previous": "...",
      "results": [
        {
          "id": 1,
          "text": "Post text",
          "timestamp": "2024-06-01T12:00:00Z",
          "author": "alice",
          "comment_count": 5,
          "comments": [
            {
              "text": "Comment text",
              "timestamp": "2024-06-01T12:05:00Z",
              "author": "bob"
            },
            ...
          ]
        },
        ...
      ]
    }
    """
    posts_qs = Post.objects.all().order_by('-timestamp')
    paginator = PostListPagination()
    page = paginator.paginate_queryset(posts_qs, request)
    serializer = [PostSerializer(post).data() for post in page]
    return paginator.get_paginated_response(serializer)




from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # password won’t be returned in responses
        }

    def create(self, validated_data):
        # Use create_user to hash password properly
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )



@api_view(['POST'])
@permission_classes([permissions.AllowAny])   
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created successfully", "user": UserSerializer(user).data},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post_view(request):
    """
    POST /api/posts/create/
    Create a new Post for the authenticated user.

    Request JSON:
    {
      "text": "Post content"
    }

    Response:
    {
      "id": "<uuid>",
      "text": "...",
      "timestamp": "...",
      "author": "<username>"
    }
    """
    text = request.data.get('text')
    if not text:
        return Response({"error": "Text is required."}, status=status.HTTP_400_BAD_REQUEST)
    post = Post.objects.create(text=text, user=request.user)
    return Response({
        "id": post.id,
        "text": post.text,
        "timestamp": post.timestamp,
        "author": post.user.username
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_view(request):
    """
    POST /api/login/
    Authenticate user.

    Request JSON:
    {
      "username": "...",
      "password": "..."
    }

    Response (success):
    {
      "message": "Login successful."
    }

    Response (failure):
    {
      "error": "Invalid credentials."
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment_view(request):
    """
    POST /api/comments/add/
    Add a comment to a post for the authenticated user.

    Request JSON:
    {
      "post_id": "<uuid>",
      "text": "Comment content"
    }

    Response:
    {
      "id": "<uuid>",
      "text": "...",
      "timestamp": "...",
      "post_id": "<uuid>",
      "author": "<username>"
    }
    """
    post_id = request.data.get('post_id')
    text = request.data.get('text')
    if not post_id or not text:
        return Response({"error": "post_id and text are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    comment = Comment.objects.create(post=post, text=text, user=request.user)
    print( "Comment created:", comment)
    return Response({
        "id": comment.id,
        "text": comment.text,
        "timestamp": comment.timestamp,
        "post_id": str(post.id),
        "author": comment.user.username
    }, status=status.HTTP_201_CREATED)
