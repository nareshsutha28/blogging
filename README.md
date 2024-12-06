# Blogging API Project

## Overview
This is a blogging API project built with Django and Django Rest Framework (DRF). The API allows users to create and manage blog posts, comment on posts, and retrieve top commented posts. It also supports user authentication with JWT tokens.

## Features
- **User Authentication**: JWT-based login and authentication.
- **Post Management**: Create, retrieve, update, and delete blog posts.
- **Commenting**: Users can comment on posts, with pagination on comments.
- **Top Commented Posts**: Fetch the top five posts with the most comments.

## Project Setup

### 1. Clone the Repository

Clone the project repository from GitHub to your local machine:

```bash
git clone https://github.com/nareshsutha28/blogging.git
cd blogging
```

### 2. Create a Virtual Environment
Create a virtual environment to isolate your project dependencies:
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
Activate the virtual environment:

```bash
venv\Scripts\activate
```

### 4. Install Python Dependencies
Install all the required dependencies listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```

### 5. Create a .env File
Create a .env file in the root directory of the project and add your PostgreSQL credentials like the following:
```base
DB_NAME="blogging_db"
DB_USERNAME="postgres"
PASSWORD="postgres"
HOST="localhost"
PORT=5432
```

### 6. Run Database Migrations
Run the following command to apply all the database migrations:

```bash
python manage.py migrate
```

### 7. Create a Superuser (Optional)
If you want to access the Django admin, you can create a superuser:

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server
Start the development server to run the project locally:

```bash
python manage.py runserver
```

### 9. Swagger user Interface
to get swagger user interface 
```bash
http://localhost:8000/swagger/
```
