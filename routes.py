import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

from app import db
from models import User, Submission
from forms import SetupForm, LoginForm, CreateUserForm, SubmissionForm, ReviewSubmissionForm
from utils import is_setup_required, create_admin_user, update_user_login_time, save_image, get_user_stats

def register_routes(app):
    
    # Context processor to add common variables to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    @app.route('/')
    def index():
        if is_setup_required():
            return redirect(url_for('setup'))
        
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        
        return redirect(url_for('login'))
    
    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        # Redirect if already set up
        if not is_setup_required():
            flash('System is already configured', 'info')
            return redirect(url_for('index'))
        
        form = SetupForm()
        
        if form.validate_on_submit():
            admin = create_admin_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            
            flash('Administrator account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('setup.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if is_setup_required():
            return redirect(url_for('setup'))
        
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                update_user_login_time(user)
                
                flash(f'Welcome back, {user.username}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'success')
        return redirect(url_for('login'))
    
    # Admin routes
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied: You must be an administrator to view this page', 'danger')
            return redirect(url_for('index'))
        
        stats = get_user_stats()
        
        # Get pending submissions for quick access
        pending_submissions = Submission.query.filter_by(status="pending").order_by(Submission.created_at.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html', stats=stats, pending_submissions=pending_submissions)
    
    @app.route('/admin/create-user', methods=['GET', 'POST'])
    @login_required
    def create_user():
        if current_user.role != 'admin':
            flash('Access denied: You must be an administrator to view this page', 'danger')
            return redirect(url_for('index'))
        
        form = CreateUserForm()
        
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                role='user'
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User {form.username.data} has been created successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/create_user.html', form=form)
    
    @app.route('/admin/users')
    @login_required
    def manage_users():
        if current_user.role != 'admin':
            flash('Access denied: You must be an administrator to view this page', 'danger')
            return redirect(url_for('index'))
        
        users = User.query.filter_by(role='user').order_by(User.username).all()
        return render_template('admin/create_user.html', users=users, form=CreateUserForm())
    
    @app.route('/admin/submissions')
    @login_required
    def admin_submissions():
        if current_user.role != 'admin':
            flash('Access denied: You must be an administrator to view this page', 'danger')
            return redirect(url_for('index'))
        
        status_filter = request.args.get('status', '')
        
        query = Submission.query
        
        if status_filter and status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        submissions = query.order_by(Submission.created_at.desc()).all()
        
        return render_template('admin/submissions.html', submissions=submissions, status_filter=status_filter)
    
    @app.route('/admin/submission/<int:submission_id>', methods=['GET', 'POST'])
    @login_required
    def review_submission(submission_id):
        if current_user.role != 'admin':
            flash('Access denied: You must be an administrator to view this page', 'danger')
            return redirect(url_for('index'))
        
        submission = Submission.query.get_or_404(submission_id)
        form = ReviewSubmissionForm()
        
        if form.validate_on_submit():
            submission.status = form.status.data
            submission.admin_comment = form.comment.data
            submission.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Submission has been reviewed successfully', 'success')
            return redirect(url_for('admin_submissions'))
        
        # Pre-fill the form with existing data
        if request.method == 'GET':
            form.submission_id.data = submission.id
            if submission.status != 'pending':
                form.status.data = submission.status
                form.comment.data = submission.admin_comment
        
        return render_template('admin/review_submission.html', submission=submission, form=form)
    
    # User routes
    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if current_user.role != 'user':
            return redirect(url_for('admin_dashboard'))
        
        submissions = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.created_at.desc()).all()
        
        return render_template('user/dashboard.html', submissions=submissions)
    
    @app.route('/user/create-submission', methods=['GET', 'POST'])
    @login_required
    def create_submission():
        if current_user.role != 'user':
            return redirect(url_for('admin_dashboard'))
        
        form = SubmissionForm()
        
        if form.validate_on_submit():
            # Handle image upload if provided
            image_path = None
            if form.image.data:
                image_path = save_image(form.image.data)
            
            submission = Submission(
                user_id=current_user.id,
                caption=form.caption.data,
                image_path=image_path,
                status='pending'
            )
            
            # Store encrypted version of the caption
            submission.encrypted_caption = form.caption.data
            
            db.session.add(submission)
            db.session.commit()
            
            flash('Your submission has been received and is pending review', 'success')
            return redirect(url_for('user_dashboard'))
        
        return render_template('user/create_submission.html', form=form)
    
    @app.route('/user/submission/<int:submission_id>')
    @login_required
    def submission_details(submission_id):
        submission = Submission.query.get_or_404(submission_id)
        
        # Ensure the user can only see their own submissions
        if current_user.role != 'admin' and submission.user_id != current_user.id:
            abort(403)
        
        return render_template('user/submission_details.html', submission=submission)
    
    @app.route('/user/edit-submission/<int:submission_id>', methods=['GET', 'POST'])
    @login_required
    def edit_submission(submission_id):
        if current_user.role != 'user':
            return redirect(url_for('admin_dashboard'))
        
        submission = Submission.query.get_or_404(submission_id)
        
        # Ensure the user can only edit their own submissions
        if submission.user_id != current_user.id:
            abort(403)
        
        # Can only edit if status is "needs_edits"
        if submission.status != 'needs_edits':
            flash('This submission cannot be edited', 'danger')
            return redirect(url_for('submission_details', submission_id=submission_id))
        
        form = SubmissionForm()
        
        if form.validate_on_submit():
            # Handle image upload if provided
            if form.image.data:
                image_path = save_image(form.image.data)
                submission.image_path = image_path
            
            submission.caption = form.caption.data
            submission.encrypted_caption = form.caption.data
            submission.status = 'pending'  # Reset to pending after edit
            submission.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Your submission has been updated and is pending review', 'success')
            return redirect(url_for('user_dashboard'))
        
        # Pre-fill the form with existing data
        elif request.method == 'GET':
            form.caption.data = submission.caption
        
        return render_template('user/create_submission.html', form=form, submission=submission, is_edit=True)
    
    # Utility routes
    @app.route('/uploads/<path:filename>')
    @login_required
    def uploaded_file(filename):
        return send_from_directory(
            os.path.join(current_app.root_path, 'static/uploads'),
            filename
        )
