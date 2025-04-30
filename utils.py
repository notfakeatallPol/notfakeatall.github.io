import os
import secrets
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
import base64
from cryptography.fernet import Fernet
from models import SystemConfig, User, db

def get_unique_filename(filename):
    """Generate a unique filename to prevent overwriting."""
    _, ext = os.path.splitext(filename)
    return secure_filename(f"{secrets.token_hex(8)}{ext}")

def save_image(file):
    """Save an uploaded image and return the path."""
    if not file:
        return None
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename and save the file
    filename = get_unique_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # Return the relative path for storage in the database
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

def is_setup_required():
    """Check if initial setup is required (no admin exists)."""
    return current_app.config.get("SETUP_REQUIRED", True)

def create_admin_user(username, email, password):
    """Create the initial admin user during setup."""
    admin = User(username=username, email=email, role="admin")
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    # Generate encryption key if it doesn't exist
    if not SystemConfig.get('encryption_key'):
        encryption_key = Fernet.generate_key().decode()
        SystemConfig.set('encryption_key', encryption_key)
    
    # Set setup as completed
    current_app.config["SETUP_REQUIRED"] = False
    
    return admin

def update_user_login_time(user):
    """Update the last login time for a user."""
    user.last_login = datetime.utcnow()
    db.session.commit()

def get_user_stats():
    """Get statistics for admin dashboard."""
    from models import Submission
    
    total_users = User.query.filter_by(role="user").count()
    total_submissions = Submission.query.count()
    pending_submissions = Submission.query.filter_by(status="pending").count()
    accepted_submissions = Submission.query.filter_by(status="accepted").count()
    rejected_submissions = Submission.query.filter_by(status="rejected").count()
    needs_edits_submissions = Submission.query.filter_by(status="needs_edits").count()
    
    return {
        "total_users": total_users,
        "total_submissions": total_submissions,
        "pending_submissions": pending_submissions,
        "accepted_submissions": accepted_submissions,
        "rejected_submissions": rejected_submissions,
        "needs_edits_submissions": needs_edits_submissions
    }
