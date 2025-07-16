from src.models.user import db
from datetime import datetime

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)  # If posted by vendor
    
    # Video content
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # Duration in seconds
    
    # Video metadata
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    
    # Content categorization
    hashtags = db.Column(db.Text, nullable=True)  # Comma-separated hashtags
    cuisine_type = db.Column(db.String(100), nullable=True)
    food_category = db.Column(db.String(50), nullable=True)  # appetizer, main, dessert, etc.
    
    # Location (if different from vendor location)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(255), nullable=True)
    
    # Engagement metrics
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    likes = db.relationship('Like', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    video_menu_items = db.relationship('VideoMenuItem', backref='video', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Video {self.id} by {self.user_id}>'

    def increment_view(self):
        """Increment view count"""
        self.view_count += 1

    def update_engagement_counts(self):
        """Update engagement counts based on actual data"""
        self.like_count = self.likes.count()
        self.comment_count = self.comments.count()

    def get_hashtags_list(self):
        """Return hashtags as a list"""
        if self.hashtags:
            return [tag.strip() for tag in self.hashtags.split(',') if tag.strip()]
        return []

    def set_hashtags_from_list(self, hashtag_list):
        """Set hashtags from a list"""
        self.hashtags = ','.join(hashtag_list) if hashtag_list else None

    def to_dict(self, include_creator=True):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'vendor_id': self.vendor_id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'thumbnail_url': self.thumbnail_url,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'hashtags': self.get_hashtags_list(),
            'cuisine_type': self.cuisine_type,
            'food_category': self.food_category,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'share_count': self.share_count,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_creator and self.creator:
            result['creator'] = self.creator.to_public_dict()
            
        return result


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_like'),)

    def __repr__(self):
        return f'<Like user:{self.user_id} video:{self.video_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # For replies
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Comment {self.id} by {self.user_id}>'

    def to_dict(self, include_replies=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'like_count': self.like_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': self.user.to_public_dict() if self.user else None
        }
        
        if include_replies:
            result['replies'] = [reply.to_dict() for reply in self.replies.all()]
            
        return result


class VideoMenuItem(db.Model):
    """Link videos to menu items they feature"""
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('video_id', 'menu_item_id', name='unique_video_menu_item'),)

    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'menu_item_id': self.menu_item_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

