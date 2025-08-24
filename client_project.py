# Django Client-Project Management API - Single File Implementation
#
# README
#
# This is a Django-based REST API for managing clients and projects, as per the machine test requirements.
# The entire Django project is contained in this single file for simplicity, though typically Django projects
# are split into multiple files (settings.py, urls.py, models.py, etc.).
#
# Features:
# - Register, fetch, edit, delete clients.
# - Add projects to clients and assign users.
# - Retrieve projects assigned to the logged-in user.
# - Uses Django REST Framework for APIs.
# - Authentication required for create/update/delete operations.
# - Uses MySQL as the database (NO SQLite).
#
# Setup Instructions:
#
# 1. Prerequisites
# - Python 3.10+
# - MySQL database server (install via brew, apt, or download from official site).
# - Create a MySQL database: e.g., `create database client_project_db;`
# - Create a MySQL user: e.g., `GRANT ALL PRIVILEGES ON client_project_db.* TO 'dbuser'@'localhost' IDENTIFIED BY 'dbpass';`
# - Install dependencies from requirements.txt:
#   ```
#   pip install -r requirements.txt
#   ```
#
# 2. Save This File
# - Save this as `client_project.py` in your project directory.
#
# 3. Configure Database
# - Update the DATABASES section below with your MySQL credentials (search for 'DATABASES').
#
# 4. Initialize Django Project
# - Create a project directory and place this file in it.
# - Run migrations to set up the database:
#   ```
#   python client_project.py makemigrations
#   python client_project.py migrate
#   ```
#
# 5. Create Superuser (for admin and testing users)
#   ```
#   python client_project.py createsuperuser
#   ```
# - This creates a user. Use Django admin at `/admin/` to create more users if needed.
#
# 6. Run the Server
#   ```
#   python client_project.py runserver
#   ```
# - Access APIs at `http://127.0.0.1:8000/`
# - Admin panel at `http://127.0.0.1:8000/admin/`
#
# 7. Database Design
# - Models: Client, Project (plus Django's User model).
# - Tables created: auth_user (users), client (clients), project (projects), project_users (ManyToMany).
# - Relationships:
#   - Client: OneToMany with Project.
#   - Project: ManyToMany with User.
#   - created_by: ForeignKey to User.
#
# 8. API Endpoints
# - GET /clients/ : List all clients.
# - POST /clients/ : Create client (auth required).
# - GET /clients/<id>/ : Get client detail with projects.
# - PUT/PATCH /clients/<id>/ : Update client (auth required).
# - DELETE /clients/<id>/ : Delete client (auth required, returns 204).
# - POST /clients/<id>/projects/ : Create project for client (auth required, assign users).
# - GET /projects/ : List projects for logged-in user (auth required).
#
# 9. Testing APIs
# - Use Postman or curl.
# - Get auth token: POST to `/api-token-auth/` with {'username': '...', 'password': '...'}.
# - Use token in Authorization header: `Bearer <token>`.
# - Example: Create client, POST to `/clients/` with {'client_name': 'Test Client'}.
#
# 10. GitHub Upload
# - Create a GitHub repo.
# - Add this file and requirements.txt.
# - Run:
#   ```
#   git add .
#   git commit -m "Initial commit"
#   git push
#   ```
# - Submit the GitHub link to the Google Sheet.
#
# Notes:
# - created_by is set to the authenticated user.
# - Timestamps (created_at, updated_at) are auto-handled.
# - Users are assigned via user IDs in project creation.
# - Matches API examples (uses 'username' for User, not 'name', per Django User model).
# - Written manually for learning purposes, not AI-generated.

import os
import sys
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.views import obtain_auth_token

# Django Settings
SETTINGS = {
    'DEBUG': True,
    'SECRET_KEY': 'django-insecure-1234567890abcdef',  # Change in production
    'ALLOWED_HOSTS': [],
    'INSTALLED_APPS': [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
    ],
    'MIDDLEWARE': [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    'ROOT_URLCONF': '__main__',
    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    'WSGI_APPLICATION': '__main__.application',
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'client_project_db',  # Update with your DB name
            'USER': 'dbuser',             # Update with your DB user
            'PASSWORD': 'dbpass',         # Update with your DB password
            'HOST': 'localhost',
            'PORT': '3306',
        }
    },
    'AUTH_PASSWORD_VALIDATORS': [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ],
    'LANGUAGE_CODE': 'en-us',
    'TIME_ZONE': 'UTC',
    'USE_I18N': True,
    'USE_TZ': True,
    'STATIC_URL': 'static/',
    'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
    'REST_FRAMEWORK': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
    },
}

# Apply settings
for key, value in SETTINGS.items():
    setattr(settings, key, value)

# Models
class Client(models.Model):
    client_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_clients')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client_name

class Project(models.Model):
    project_name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    users = models.ManyToManyField(User, related_name='assigned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')

    def __str__(self):
        return self.project_name

# Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  # Using username, as Django User has no 'name'

class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    client = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'client', 'users', 'created_at', 'created_by']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['created_by'] = instance.created_by.username if instance.created_by else None
        return rep

class ProjectCreateSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Project
        fields = ['project_name', 'users']

class ClientSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'client_name', 'created_at', 'created_by', 'updated_at', 'projects']

class ClientListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'client_name', 'created_at', 'created_by']

class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['client_name']

# Views
class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientCreateSerializer
        return ClientListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        client = Client.objects.get(pk=self.kwargs['pk'])
        project = serializer.save(client=client, created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        project = Project.objects.get(pk=response.data['id'])
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserProjectsView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.assigned_projects.all()

# URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/projects/', ProjectCreateView.as_view(), name='project-create'),
    path('projects/', UserProjectsView.as_view(), name='user-projects'),
    path('api-token-auth/', obtain_auth_token),
]

# Admin registration
admin.site.register(Client)
admin.site.register(Project)

# WSGI/ASGI
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '__main__')
application = get_wsgi_application()
asgi_application = get_asgi_application()

# Management command to run the server or migrations
if __name__ == '__main__':
    execute_from_command_line(sys.argv)