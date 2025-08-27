from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()

class PostStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    linkedin_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with posts
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Enum(PostStatus), default=PostStatus.DRAFT, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=True)
    published_time = db.Column(db.DateTime, nullable=True)
    linkedin_post_id = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.id}: {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'image_path': self.image_path,
            'status': self.status.value,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'published_time': self.published_time.isoformat() if self.published_time else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

def init_db(app):
    """Initialize the database"""
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables (only creates if they don't exist)
            db.create_all()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Database initialization note: {e}")
            print("Database tables may already exist - continuing...")

def get_user_stats(user_id):
    """Get statistics for a user's posts"""
    total_posts = Post.query.filter_by(user_id=user_id).count()
    published_posts = Post.query.filter_by(user_id=user_id, status=PostStatus.PUBLISHED).count()
    scheduled_posts = Post.query.filter_by(user_id=user_id, status=PostStatus.SCHEDULED).count()
    failed_posts = Post.query.filter_by(user_id=user_id, status=PostStatus.FAILED).count()
    
    return {
        'total': total_posts,
        'published': published_posts,
        'scheduled': scheduled_posts,
        'failed': failed_posts,
        'success_rate': round((published_posts / total_posts * 100) if total_posts > 0 else 0, 2)
    }
