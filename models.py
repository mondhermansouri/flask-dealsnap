from app import db
from datetime import datetime
from sqlalchemy import Index
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    original_title = db.Column(db.String(200), nullable=True)
    ai_headline = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Float, nullable=True)
    original_price = db.Column(db.Float, nullable=True)
    discount_percentage = db.Column(db.Integer, nullable=True)

    affiliate_url = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

    category = db.Column(db.String(50), nullable=False, default="electronics", index=True)
    source = db.Column(db.String(50), nullable=False, default="amazon", index=True)

    rating = db.Column(db.Float, nullable=True)
    num_reviews = db.Column(db.Integer, nullable=True)

    is_active = db.Column(db.Boolean, default=True, index=True)
    featured = db.Column(db.Boolean, default=False, index=True)

    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Analytics
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Deal {self.title}>"

    def to_dict(self):
        """Convertir l'objet en dictionnaire JSON-friendly"""
        return {
            "id": self.id,
            "title": self.title,
            "original_title": self.original_title,
            "ai_headline": self.ai_headline,
            "description": self.description,
            "price": self.price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "affiliate_url": self.affiliate_url,
            "image_url": self.image_url,
            "category": self.category,
            "source": self.source,
            "rating": self.rating,
            "num_reviews": self.num_reviews,
            "is_active": self.is_active,
            "featured": self.featured,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "views": self.views,
            "clicks": self.clicks,
        }


# Ajout d’index utiles pour optimiser les requêtes
Index("idx_deals_category", Deal.category)
Index("idx_deals_source", Deal.source)
Index("idx_deals_active", Deal.is_active)
Index("idx_deals_featured", Deal.featured)


class ClickEvent(db.Model):
    __tablename__ = "click_events"

    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id"), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    deal = db.relationship("Deal", backref=db.backref("click_events", lazy=True))

    def __repr__(self):
        return f"<ClickEvent deal_id={self.deal_id} ip={self.ip_address}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(db.String(20), default="admin")  # admin / user (extensible)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        """Hash du mot de passe"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Vérifie si l'utilisateur est admin"""
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"
