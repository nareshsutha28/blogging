"""
URL configuration for blogging project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from user.views import (RegisterUserView, LoginAPIView,
                         CustomRefreshTokenView, LogoutApiView)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Blogging API",
        default_version='v1',
        description="API documentation for the Blogging project",
        terms_of_service="",
        contact=openapi.Contact(email="contact@blogging.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # User Registration and Authentication related urls
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginAPIView.as_view(), name='login_user'),
    path('refresh-token/', CustomRefreshTokenView.as_view(), name='refresh_token'),
    path('logout/', LogoutApiView.as_view(), name='logout_user'),

    # Swagger related urls
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
