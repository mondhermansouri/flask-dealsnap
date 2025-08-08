from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    original_title = db.Column(db.String(200), nullable=True)
    ai_headline = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    original_price = db.Column(db.Float, nullable=True)
    discount_percentage = db.Column(db.Integer, nullable=True)
    affiliate_url = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='electronics')
    source = db.Column(db.String(50), nullable=False, default='amazon')
    rating = db.Column(db.Float, nullable=True)
    num_reviews = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Analytics
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Deal {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'ai_headline': self.ai_headline,
            'description': self.description,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'affiliate_url': self.affiliate_url,
            'image_url': self.image_url,
            'category': self.category,
            'source': self.source,
            'rating': self.rating,
            'num_reviews': self.num_reviews,
            'featured': self.featured,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'views': self.views,
            'clicks': self.clicks
        }

class ClickEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    deal = db.relationship('Deal', backref=db.backref('click_events', lazy=True))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)  # For simplicity, all users are admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
