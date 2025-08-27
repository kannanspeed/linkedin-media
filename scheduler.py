from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import atexit
import os
from database import db, Post, PostStatus, User
from linkedin_api import LinkedInAPI
from config import Config

class PostScheduler:
    def __init__(self, app=None):
        self.scheduler = None
        self.linkedin_api = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the scheduler with the Flask app"""
        # Configure job stores and executors
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        # Initialize LinkedIn API
        self.linkedin_api = LinkedInAPI(
            app.config['LINKEDIN_CLIENT_ID'],
            app.config['LINKEDIN_CLIENT_SECRET'],
            app.config['LINKEDIN_REDIRECT_URI']
        )
        
        # Start scheduler
        self.scheduler.start()
        
        # Shutdown scheduler when app exits
        atexit.register(lambda: self.scheduler.shutdown())
        
        print("Post scheduler initialized successfully!")
    
    def schedule_post(self, post_id, scheduled_time):
        """Schedule a post to be published"""
        try:
            job_id = f"post_{post_id}"
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Schedule new job
            self.scheduler.add_job(
                func=self.publish_post,
                trigger='date',
                run_date=scheduled_time,
                args=[post_id],
                id=job_id,
                replace_existing=True
            )
            
            print(f"Post {post_id} scheduled for {scheduled_time}")
            return True
        except Exception as e:
            print(f"Error scheduling post {post_id}: {e}")
            return False
    
    def cancel_scheduled_post(self, post_id):
        """Cancel a scheduled post"""
        try:
            job_id = f"post_{post_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                print(f"Cancelled scheduled post {post_id}")
                return True
            return False
        except Exception as e:
            print(f"Error cancelling post {post_id}: {e}")
            return False
    
    def publish_post(self, post_id):
        """Publish a scheduled post"""
        print(f"Attempting to publish post {post_id}")
        
        try:
            # Get post from database
            post = Post.query.get(post_id)
            if not post:
                print(f"Post {post_id} not found")
                return
            
            # Get user
            user = User.query.get(post.user_id)
            if not user:
                print(f"User for post {post_id} not found")
                return
            
            # Check if user's token is still valid
            if user.token_expires_at and user.token_expires_at < datetime.utcnow():
                print(f"Access token expired for user {user.id}")
                post.status = PostStatus.FAILED
                post.error_message = "Access token expired. Please reconnect your LinkedIn account."
                db.session.commit()
                return
            
            # Upload image if exists
            image_asset_id = None
            if post.image_path:
                image_path = os.path.join('static', post.image_path.lstrip('/static/'))
                if os.path.exists(image_path):
                    image_asset_id = self.linkedin_api.upload_image(
                        user.access_token,
                        image_path,
                        user.linkedin_id
                    )
                    if not image_asset_id:
                        print(f"Failed to upload image for post {post_id}")
                        post.status = PostStatus.FAILED
                        post.error_message = "Failed to upload image to LinkedIn"
                        post.retry_count += 1
                        db.session.commit()
                        
                        # Retry if less than 3 attempts
                        if post.retry_count < 3:
                            self.schedule_retry(post_id, minutes=30)
                        return
            
            # Create the post
            linkedin_post_id = self.linkedin_api.create_post(
                user.access_token,
                user.linkedin_id,
                post.content,
                image_asset_id
            )
            
            if linkedin_post_id:
                # Update post status
                post.status = PostStatus.PUBLISHED
                post.published_time = datetime.utcnow()
                post.linkedin_post_id = linkedin_post_id
                post.error_message = None
                print(f"Successfully published post {post_id} to LinkedIn")
            else:
                # Mark as failed
                post.status = PostStatus.FAILED
                post.error_message = "Failed to create post on LinkedIn"
                post.retry_count += 1
                print(f"Failed to publish post {post_id}")
                
                # Retry if less than 3 attempts
                if post.retry_count < 3:
                    self.schedule_retry(post_id, minutes=30)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error publishing post {post_id}: {e}")
            try:
                post = Post.query.get(post_id)
                if post:
                    post.status = PostStatus.FAILED
                    post.error_message = str(e)
                    post.retry_count += 1
                    db.session.commit()
                    
                    # Retry if less than 3 attempts
                    if post.retry_count < 3:
                        self.schedule_retry(post_id, minutes=30)
            except Exception as db_error:
                print(f"Error updating post status: {db_error}")
    
    def schedule_retry(self, post_id, minutes=30):
        """Schedule a retry for a failed post"""
        try:
            retry_time = datetime.utcnow().replace(second=0, microsecond=0)
            retry_time = retry_time.replace(minute=retry_time.minute + minutes)
            
            job_id = f"retry_post_{post_id}"
            
            self.scheduler.add_job(
                func=self.publish_post,
                trigger='date',
                run_date=retry_time,
                args=[post_id],
                id=job_id,
                replace_existing=True
            )
            
            print(f"Scheduled retry for post {post_id} at {retry_time}")
        except Exception as e:
            print(f"Error scheduling retry for post {post_id}: {e}")
    
    def get_scheduled_jobs(self):
        """Get all scheduled jobs"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'next_run_time': job.next_run_time,
                    'args': job.args
                })
            return jobs
        except Exception as e:
            print(f"Error getting scheduled jobs: {e}")
            return []
    
    def reschedule_post(self, post_id, new_time):
        """Reschedule an existing post"""
        try:
            # Cancel existing schedule
            self.cancel_scheduled_post(post_id)
            
            # Schedule for new time
            return self.schedule_post(post_id, new_time)
        except Exception as e:
            print(f"Error rescheduling post {post_id}: {e}")
            return False
