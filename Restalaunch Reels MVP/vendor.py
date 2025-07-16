from src.models.user import db
from datetime import datetime

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)  # restaurant, food_truck, street_vendor, catering, etc.
    description = db.Column(db.Text, nullable=True)
    cuisine_type = db.Column(db.String(100), nullable=True)  # italian, mexican, asian, etc.
    
    # Location information
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Contact information
    phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    
    # Business hours (JSON string)
    business_hours = db.Column(db.Text, nullable=True)  # Store as JSON
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Ratings and metrics
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_items = db.relationship('MenuItem', backref='vendor', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='vendor', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Vendor {self.business_name}>'

    def update_rating(self):
        """Update average rating based on reviews"""
        reviews = self.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = total_rating / len(reviews)
            self.total_reviews = len(reviews)
        else:
            self.average_rating = 0.0
            self.total_reviews = 0

    def get_distance_from(self, lat, lng):
        """Calculate distance from given coordinates (simplified)"""
        if not self.latitude or not self.longitude:
            return None
        
        # Simple distance calculation (not accurate for long distances)
        import math
        lat_diff = self.latitude - lat
        lng_diff = self.longitude - lng
        return math.sqrt(lat_diff**2 + lng_diff**2) * 111  # Rough km conversion

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'business_type': self.business_type,
            'description': self.description,
            'cuisine_type': self.cuisine_type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'website': self.website,
            'business_hours': self.business_hours,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=True)  # appetizer, main, dessert, drink, etc.
    image_url = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    
    # Dietary information
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_spicy = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MenuItem {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'is_vegetarian': self.is_vegetarian,
            'is_vegan': self.is_vegan,
            'is_gluten_free': self.is_gluten_free,
            'is_spicy': self.is_spicy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='reviews')

    def __repr__(self):
        return f'<Review {self.rating} stars for vendor {self.vendor_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_public_dict() if self.user else None
        }

