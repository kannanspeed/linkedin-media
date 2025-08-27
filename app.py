from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image

# Import our modules
# Use production config if FLASK_ENV is set to production
if os.environ.get('FLASK_ENV') == 'production':
    from config_production import Config
else:
    try:
        from config_local import Config
    except ImportError:
        from config import Config
from database import db, init_db, User, Post, PostStatus, get_user_stats
from linkedin_api import LinkedInAPI
from scheduler import PostScheduler

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.login_message = 'Please connect your LinkedIn account to access this page.'

# Initialize database
init_db(app)

# Initialize LinkedIn API
linkedin_api = LinkedInAPI(
    app.config['LINKEDIN_CLIENT_ID'],
    app.config['LINKEDIN_CLIENT_SECRET'],
    app.config['LINKEDIN_REDIRECT_URI']
)

# Initialize scheduler
post_scheduler = PostScheduler(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_path, max_size=(1200, 1200)):
    """Resize image to fit within max_size while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
        return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

# Routes
@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/auth/linkedin')
def linkedin_auth():
    """Initiate LinkedIn OAuth"""
    auth_url = linkedin_api.get_authorization_url(state=str(uuid.uuid4()))
    return redirect(auth_url)

@app.route('/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'LinkedIn authentication failed: {error}', 'error')
        return redirect(url_for('index'))
    
    if not code:
        flash('No authorization code received from LinkedIn', 'error')
        return redirect(url_for('index'))
    
    # Get access token
    token_data = linkedin_api.get_access_token(code)
    if not token_data:
        flash('Failed to get access token from LinkedIn', 'error')
        return redirect(url_for('index'))
    
    # Get user profile
    profile_data = linkedin_api.get_user_profile(token_data['access_token'])
    if not profile_data:
        flash('Failed to get profile information from LinkedIn', 'error')
        return redirect(url_for('index'))
    
    # Check if user already exists
    user = User.query.filter_by(linkedin_id=profile_data['id']).first()
    
    if user:
        # Update existing user
        user.access_token = token_data['access_token']
        user.refresh_token = token_data.get('refresh_token')
        user.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
        user.last_login = datetime.utcnow()
        user.name = profile_data['name']
        user.email = profile_data.get('email')
        user.profile_picture = profile_data.get('profile_picture')
    else:
        # Create new user
        user = User(
            linkedin_id=profile_data['id'],
            name=profile_data['name'],
            email=profile_data.get('email'),
            profile_picture=profile_data.get('profile_picture'),
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
        )
        db.session.add(user)
    
    db.session.commit()
    login_user(user)
    flash('Successfully connected to LinkedIn!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('Successfully logged out!', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get user's posts
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    
    # Get statistics
    stats = get_user_stats(current_user.id)
    
    # Get scheduled posts for calendar
    scheduled_posts = Post.query.filter_by(
        user_id=current_user.id,
        status=PostStatus.SCHEDULED
    ).order_by(Post.scheduled_time.asc()).all()
    
    return render_template('dashboard.html', 
                         posts=posts, 
                         stats=stats, 
                         scheduled_posts=scheduled_posts)

@app.route('/create-post')
@login_required
def create_post():
    """Create new post page"""
    return render_template('create_post.html')

@app.route('/api/posts', methods=['POST'])
@login_required
def api_create_post():
    """API endpoint to create a new post"""
    try:
        content = request.form.get('content', '').strip()
        scheduled_time_str = request.form.get('scheduled_time')
        
        if not content:
            return jsonify({'error': 'Post content is required'}), 400
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
                
                # Save file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Resize image
                if resize_image(file_path):
                    image_path = f"uploads/{unique_filename}"
                else:
                    os.remove(file_path)
                    return jsonify({'error': 'Failed to process image'}), 400
        
        # Parse scheduled time
        scheduled_time = None
        if scheduled_time_str:
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                if scheduled_time <= datetime.utcnow():
                    return jsonify({'error': 'Scheduled time must be in the future'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid scheduled time format'}), 400
        
        # Create post
        post = Post(
            user_id=current_user.id,
            content=content,
            image_path=image_path,
            status=PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT,
            scheduled_time=scheduled_time
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Schedule post if time is specified
        if scheduled_time:
            if post_scheduler.schedule_post(post.id, scheduled_time):
                flash('Post scheduled successfully!', 'success')
            else:
                post.status = PostStatus.DRAFT
                db.session.commit()
                flash('Failed to schedule post. Saved as draft.', 'warning')
        else:
            flash('Post saved as draft!', 'info')
        
        return jsonify({
            'success': True,
            'post_id': post.id,
            'redirect': url_for('dashboard')
        })
        
    except Exception as e:
        print(f"Error creating post: {e}")
        return jsonify({'error': 'An error occurred while creating the post'}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    """API endpoint to delete a post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    try:
        # Cancel scheduled job if exists
        if post.status == PostStatus.SCHEDULED:
            post_scheduler.cancel_scheduled_post(post.id)
        
        # Delete image file if exists
        if post.image_path:
            image_file_path = os.path.join('static', post.image_path.lstrip('/static/'))
            if os.path.exists(image_file_path):
                os.remove(image_file_path)
        
        # Delete post
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error deleting post: {e}")
        return jsonify({'error': 'Failed to delete post'}), 500

@app.route('/api/posts/<int:post_id>/publish', methods=['POST'])
@login_required
def api_publish_post(post_id):
    """API endpoint to publish a post immediately"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    if post.status not in [PostStatus.DRAFT, PostStatus.FAILED]:
        return jsonify({'error': 'Post cannot be published'}), 400
    
    try:
        # Update post status and schedule for immediate publishing
        post.status = PostStatus.SCHEDULED
        post.scheduled_time = datetime.utcnow()
        db.session.commit()
        
        # Schedule immediately
        if post_scheduler.schedule_post(post.id, datetime.utcnow()):
            return jsonify({'success': True, 'message': 'Post is being published...'})
        else:
            post.status = PostStatus.DRAFT
            db.session.commit()
            return jsonify({'error': 'Failed to schedule post for publishing'}), 500
            
    except Exception as e:
        print(f"Error publishing post: {e}")
        return jsonify({'error': 'Failed to publish post'}), 500

@app.route('/api/posts/<int:post_id>/reschedule', methods=['POST'])
@login_required
def api_reschedule_post(post_id):
    """API endpoint to reschedule a post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    scheduled_time_str = request.json.get('scheduled_time')
    if not scheduled_time_str:
        return jsonify({'error': 'Scheduled time is required'}), 400
    
    try:
        scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
        if scheduled_time <= datetime.utcnow():
            return jsonify({'error': 'Scheduled time must be in the future'}), 400
        
        # Update post
        post.scheduled_time = scheduled_time
        post.status = PostStatus.SCHEDULED
        db.session.commit()
        
        # Reschedule
        if post_scheduler.reschedule_post(post.id, scheduled_time):
            return jsonify({'success': True, 'message': 'Post rescheduled successfully'})
        else:
            return jsonify({'error': 'Failed to reschedule post'}), 500
            
    except ValueError:
        return jsonify({'error': 'Invalid scheduled time format'}), 400
    except Exception as e:
        print(f"Error rescheduling post: {e}")
        return jsonify({'error': 'Failed to reschedule post'}), 500

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint to get user statistics"""
    stats = get_user_stats(current_user.id)
    return jsonify(stats)

@app.route('/analytics')
@login_required
def analytics():
    """Analytics page"""
    stats = get_user_stats(current_user.id)
    
    # Get recent posts for detailed analytics
    recent_posts = Post.query.filter_by(user_id=current_user.id)\
                           .filter(Post.status.in_([PostStatus.PUBLISHED, PostStatus.FAILED]))\
                           .order_by(Post.created_at.desc())\
                           .limit(20).all()
    
    return render_template('analytics.html', stats=stats, recent_posts=recent_posts)

if __name__ == '__main__':
    print("Starting LinkedIn Scheduler App...")
    
    # Check if we're in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if not is_production:
        print(f"Make sure to set your LinkedIn OAuth credentials in the .env file or environment variables")
    
    print(f"Redirect URI should be: {app.config['LINKEDIN_REDIRECT_URI']}")
    
    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))
    
    if is_production:
        # Production mode - use gunicorn
        print("Running in production mode")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode
        print("Running in development mode")
        app.run(debug=True, host='0.0.0.0', port=port)
