# Banking Project

## Overview

The banking project is a web application developed with Django and Django REST framework, designed to provide essential banking functionalities. The system incorporates user authentication, role-based access control, and various views for bankers and clients.

## Key Features

- **User Roles:** The application supports different user roles, distinguishing between bankers and clients, each having specific permissions.

- **Client Operations:** Clients can request bank accounts, debit cards, and manage their accounts through dedicated views. The system ensures that clients have a secure and straightforward experience.

- **Banker Operations:** Bankers, with elevated permissions, can view a list of clients and create new client accounts. They play a crucial role in approving client requests.

- **Security:** The project includes measures to ensure data security, including user authentication, permission checks, and validation of sensitive operations.

- **API Endpoints:** Utilizing Django REST framework, the project exposes API endpoints for creating and retrieving user data, making transaction, withdraws, deposit and managing bank accounts, and handling debit card requests.

## Technology Stack

- **Backend Framework:** Django with Django REST framework
- **Database:** Django ORM with MySQL
- **User Authentication:** Django built-in authentication system(JWT)
- **API Development:** Django REST framework for building robust and scalable APIs

## Testing

- **Pytest:** The project includes comprehensive test cases using Pytest to ensure the reliability and correctness of the implemented features.

## Getting Started

To get started with the project, follow these steps:


# Setup

### Cloning the repository

1. Clone the repository:

        git clone <repository_url>

2. Create and activate a virtual environment (optional, but recommended):

       python3 -m venv env

       source env/bin/activate # On macOS/Linux

       .\env\Scripts\activate # On Windows

3. Install the project dependencies:

       pip install -r requirements.txt

4. Make migrations 
   
       python manage.py runserver

5. Start the development server:

       python manage.py runserver
6. Access the application in your web browser at `http://localhost:8000/api/`.

> ⚠ Then, the development server will be started at http://127.0.0.1:8000/


# Structure
The project follows the Django project structure, where the base functionality is placed in the "base" app, and the specific models, views, and URLs are defined in the "api" app.