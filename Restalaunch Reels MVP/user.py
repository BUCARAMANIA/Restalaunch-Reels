from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_vendor = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor_profile = db.relationship('Vendor', backref='user', uselist=False, cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    follows = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.follows.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def is_following(self, user):
        return self.follows.filter_by(followed_id=user.id).first() is not None

    def get_follower_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.follows.count()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'is_vendor': self.is_vendor,
            'is_verified': self.is_verified,
            'follower_count': self.get_follower_count(),
            'following_count': self.get_following_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def to_public_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'is_vendor': self.is_vendor,
            'is_verified': self.is_verified,
            'follower_count': self.get_follower_count(),
            'following_count': self.get_following_count()
        }


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)

    def to_dict(self):
        return {
            'id': self.id,
            'follower_id': self.follower_id,
            'followed_id': self.followed_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

