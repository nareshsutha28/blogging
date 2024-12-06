from rest_framework.generics import GenericAPIView
from rest_framework import status
from blogging.utils import get_response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from user.serializers import RegisterUserSerializer, LoginUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterUserView(GenericAPIView):
    
    permission_classes = [AllowAny]
    
    """
    API endpoint to register a new user using GenericAPIView.
    """
    @swagger_auto_schema(
        operation_description="Register a new user with email, first name, last name, date of birth, and password.",
        request_body=RegisterUserSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    'application/json': {
                        'status': 200,
                        'msg': 'User registered successfully!',
                        'data': {}
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request. Validation errors.",
                examples={
                    'application/json': {
                        'status': 400,
                        'msg': 'Validation errors',
                        'data': {}
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            # Save the user and return success response
            serializer.save()
            return get_response(status.HTTP_201_CREATED, "User registered successfully!", {})

        return get_response(status.HTTP_400_BAD_REQUEST, serializer.errors, {})


class LoginAPIView(GenericAPIView):

    permission_classes = [AllowAny]

    """
    API to log In a user with email and password.
    """
    @swagger_auto_schema(
        operation_description="Login API for user authentication",
        request_body=LoginUserSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "status": 200,
                        "msg": "Login successful",
                        "data": {
                            "refresh": "JWT_REFRESH_TOKEN",
                            "access": "JWT_ACCESS_TOKEN",
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid credentials",
                examples={
                    "application/json": {
                        "status": 400,
                        "msg": "Invalid email or password",
                        "data": {}
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            data = {
                    "refresh": refresh_token,
                    "access": access_token
                }
            # Custom response
            return get_response(status.HTTP_200_OK, "Login successful !", data) 

        # Custom error response
        return get_response(status.HTTP_400_BAD_REQUEST, serializer.errors, {})


class CustomRefreshTokenView(GenericAPIView):

    permission_classes = [AllowAny]
    """
    API to refresh Access token.
    """
    @swagger_auto_schema(
        operation_description="API to refresh access token using a valid refresh token",
        request_body=TokenRefreshSerializer,
        responses={
            200: openapi.Response(
                description="Access token refreshed successfully",
                examples={
                    "application/json": {
                        "status": 200,
                        "msg": "Token refreshed successfully",
                        "data": {
                            "access": "NEW_ACCESS_TOKEN"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid refresh token",
                examples={
                    "application/json": {
                        "status": 400,
                        "msg": "Invalid refresh token",
                        "data": {}
                    }
                }
            )
        }
    )
    def post(self, request):
        try:
            serializer = TokenRefreshSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                # Get the new access token from the serializer
                access_token = serializer.validated_data.get('access')
                data = {
                        "access": access_token
                    }
                return get_response(status.HTTP_200_OK, "Token refreshed successfully", data)

        except (InvalidToken, TokenError) as e:
            # Handle invalid refresh token
            return get_response(status.HTTP_400_BAD_REQUEST, e.args, {})


class LogoutApiView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    """
    API to log out a user by blacklisting their refresh token.
    """
    @swagger_auto_schema(
        operation_description="Log out user by blacklisting the provided refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "status": 200,
                        "msg": "Logout successful",
                        "data": {}
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid or expired refresh token",
                examples={
                    "application/json": {
                        "status": 400,
                        "msg": "Invalid or expired refresh token",
                        "data": {}
                    }
                }
            )
        
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return get_response(status.HTTP_400_BAD_REQUEST, "Refresh token is required", {})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            return get_response(status.HTTP_200_OK, "Logout successful", {})

        except TokenError as e:
            return get_response(status.HTTP_400_BAD_REQUEST, "Invalid or expired refresh token", {})
