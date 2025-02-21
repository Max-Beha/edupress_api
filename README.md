# EDUPRESS REST API

A powerful Django REST API for managing school courses, teachers, and students. This API provides a comprehensive solution for educational institutions to manage their courses, enrollments, and track student progress.

## Features

- **User Authentication**
  - JWT-based authentication
  - Separate roles for teachers and students
  - Secure password handling

- **Course Management**
  - Teachers can create and manage courses
  - Organize course content into sections
  - Upload and manage course materials
  - Track student progress

- **Student Features**
  - Course enrollment
  - Progress tracking
  - Access to course materials
  - View enrolled courses

## API Documentation

The API documentation is available through Swagger UI and ReDoc:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

## Tech Stack

- Django 4.x
- Django REST Framework
- SimpleJWT for authentication
- DRF-Spectacular for API documentation
- SQLite database (can be configured for other databases)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/school-rest-api.git
cd school-rest-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/register/`: Register new user
- `POST /api/login/`: Login user
- `GET /api/profile/`: Get user profile

### Courses (Teachers)
- `GET /api/courses/`: List all courses
- `POST /api/courses/`: Create new course
- `GET /api/courses/{id}/`: Get course details
- `PUT /api/courses/{id}/`: Update course
- `DELETE /api/courses/{id}/`: Delete course

### Course Sections
- `GET /api/courses/{course_id}/sections/`: List course sections
- `POST /api/courses/{course_id}/sections/`: Create new section
- `GET /api/courses/{course_id}/sections/{id}/`: Get section details

### Course Materials
- `GET /api/sections/{section_id}/materials/`: List materials
- `POST /api/sections/{section_id}/materials/`: Upload material
- `GET /api/sections/{section_id}/materials/{id}/`: Get material

### Enrollments (Students)
- `POST /api/courses/{course_id}/enroll/`: Enroll in course
- `GET /api/enrollments/`: List enrolled courses
- `POST /api/courses/{course_id}/progress/`: Update course progress

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate requests:

1. Obtain a token by logging in:
```bash
POST /api/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

2. Include the token in request headers:
```
Authorization: Bearer <your_token>
```

## User Types

### Teachers
- Can create and manage courses
- Can create course sections and materials
- Can view enrolled students

### Students
- Can enroll in courses
- Can view course materials
- Can track their progress
- Can view their enrolled courses

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 style guide for Python code.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Support

For support, email - mahkamboyevbehruz6@gmail.com or create an issue in the GitHub repository.
