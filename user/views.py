from rest_framework.generics import GenericAPIView
from user.serializers import RegisterUserSerializer
from blogging.utils import get_response
from rest_framework.permissions import AllowAny
from rest_framework import status
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
