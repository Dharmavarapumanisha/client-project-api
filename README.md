# client-project-api
Django Client-Project Management API
This repository contains a Django REST API for managing clients and projects, developed for the machine test. The entire implementation is in a single file, client_project.py, with dependencies listed in requirements.txt.
Project Overview
The API manages three entities: User (Django's default), Client, and Project, with the following features:

Register, list, retrieve, update, and delete clients.
Create projects for a client and assign users.
List projects assigned to the logged-in user.
Uses MySQL database (per requirements, no SQLite).
Authentication via token for create/update/delete operations.

Setup Instructions
Prerequisites

Python 3.10+
MySQL database server
Create a MySQL database: CREATE DATABASE client_project_db;
Create a MySQL user: GRANT ALL PRIVILEGES ON client_project_db.* TO 'dbuser'@'localhost' IDENTIFIED BY 'dbpass';

Installation

Clone the repository:git clone <your-repo-url>
cd <repo-directory>


Install dependencies:pip install -r requirements.txt


Configure MySQL in client_project.py:
Update the DATABASES section with your MySQL credentials (database name, user, password, host, port).



Database Setup
Run migrations to create tables:
python client_project.py makemigrations
python client_project.py migrate

Create Admin User
python client_project.py createsuperuser

Use the admin panel at /admin/ to manage users if needed.
Run the Server
python client_project.py runserver


APIs available at http://127.0.0.1:8000/
Admin panel at http://127.0.0.1:8000/admin/

Database Design

Tables: auth_user (Django users), client (clients), project (projects), project_users (ManyToMany).
Relationships:
Client: One-to-Many with Project.
Project: Many-to-Many with User via project_users.
created_by: ForeignKey to User for both Client and Project.



API Endpoints

GET /clients/: List all clients.
POST /clients/: Create a client (requires authentication).
GET /clients//: Retrieve client details with projects.
PUT/PATCH /clients//: Update client (requires authentication).
DELETE /clients//: Delete client (requires authentication, returns 204).
POST /clients//projects/: Create project and assign users (requires authentication).
GET /projects/: List projects for the logged-in user (requires authentication).
POST /api-token-auth/: Obtain auth token (send username/password).

Testing

Use Postman or curl to test APIs.
Get token: POST /api-token-auth/ with {'username': '...', 'password': '...'}.
Include token in headers: Authorization: Bearer <token>.
Example: Create client with POST /clients/ and {'client_name': 'Test Client'}.

Notes

Matches test API examples (uses username for User, as Django's User model has no name field).
Timestamps (created_at, updated_at) are auto-managed.
Code is written manually for clarity and learning purposes.
Submit the GitHub repo URL to the provided Google Sheet.
