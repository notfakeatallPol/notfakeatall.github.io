# Secure Submission System

A secure submission management system with admin controls, user accounts, and encrypted data storage.

## Features

- **Authentication and Access Control**
  - Secure login system with role-based access control
  - Initial setup workflow for creating the admin account
  - Admin ability to create and manage user accounts

- **User Features**
  - Secure submission system with optional image uploads
  - Encrypted data storage for sensitive information
  - Status tracking for submissions
  - Edit functionality for submissions that need changes

- **Admin Features**
  - Dashboard with submission statistics
  - Review and manage all user submissions
  - Assign status (Accepted, Rejected, Needs Edits) to submissions
  - Provide feedback comments to users

- **Security**
  - End-to-end encryption for sensitive data
  - Secure password hashing
  - Role-based access control
  - Protection against common web vulnerabilities

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with CSRF protection
- **Encryption**: cryptography library (Fernet symmetric encryption)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- pip (Python package manager)

### Local Development Setup

1. Clone the repository
   ```
   git clone https://github.com/yourusername/secure-submission-system.git
   cd secure-submission-system
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy from .env.example)
   ```
   cp .env.example .env
   # Edit .env with your database credentials and other settings
   ```

5. Run the application
   ```
   python main.py
   ```

6. Access the application at http://localhost:5000

### First Time Setup

1. When you first access the application, you'll be directed to the setup page
2. Create an admin account with a secure password
3. Log in with your new admin credentials
4. Create user accounts from the admin dashboard
5. Users can now log in and submit content

## Deployment

For production deployment instructions, see [deployment-guide.md](deployment-guide.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap for the responsive UI framework
- Flask and its extensions for the web framework
- The cryptography library for secure encryption