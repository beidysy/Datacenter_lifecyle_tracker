# PRG800 - Ticket Management System

## Overview
This is a Django-based project to manage data centers, track end-of-life (EOL) items, manage heat levels, and assign technicians to tasks.

## Features
- User authentication and role management (Admin, Technician)
- Ticket management (create, assign, and track tickets)
- Data Center EOL tracking system
- Notifications for critical events
- Heat tracking and logs for hardware components

## Installation

### Prerequisites
- Python 3.x
- Django 5.x
- Virtual Environment (recommended)

### Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    ```
2. Navigate to the project directory:
    ```bash
    cd your-repo-name
    ```
3. Create a virtual environment:
    ```bash
    python -m venv env
    ```
4. Activate the virtual environment:

    - For **Windows**:
      ```bash
      env\Scripts\activate
      ```
    - For **Linux/Mac**:
      ```bash
      source env/bin/activate
      ```

5. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

6. Run migrations:
    ```bash
    python manage.py migrate
    ```

7. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Usage
1. Create a superuser to access the admin panel:
    ```bash
    python manage.py createsuperuser
    ```
2. Navigate to `http://127.0.0.1:8000/admin/` to log in to the admin panel.

## Contributing
Feel free to submit a pull request or file an issue.

## License
[MIT](LICENSE)
