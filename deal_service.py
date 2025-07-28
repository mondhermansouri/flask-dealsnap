import logging
from app import db
from models import Deal
from ai_service import AIService
from datetime import datetime, timedelta

class DealService:
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_sample_deals(self):
        """Generate sample tech deals with realistic data"""
        sample_deals = [
            {
                'title': 'Apple AirPods Pro (2nd Generation)',
                'description': 'Active Noise Cancellation, Transparency Mode, Personalized Spatial Audio, up to 30 hours total listening time',
                'price': 199.99,
                'original_price': 249.99,
                'category': 'headphones',
                'source': 'amazon',
                'rating': 4.5,
                'num_reviews': 15420,
                'affiliate_url': 'https://amazon.com/dp/B0BDHWDR12',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61SUj2aKoEL._AC_SL1500_.jpg',
                'featured': True
            },
            {
                'title': 'Samsung Galaxy S24 Ultra 256GB',
                'description': 'AI-powered smartphone with S Pen, 200MP camera, 6.8" Dynamic AMOLED display',
                'price': 1099.99,
                'original_price': 1299.99,
                'category': 'smartphones',
                'source': 'amazon',
                'rating': 4.6,
                'num_reviews': 8934,
                'affiliate_url': 'https://amazon.com/dp/B0CMDRCZBR',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/71gm8v4uPJL._AC_SL1500_.jpg',
                'featured': True
            },
            {
                'title': 'MacBook Air M3 13-inch 256GB',
                'description': 'Apple M3 chip, 13.6-inch Liquid Retina display, 18-hour battery life, midnight color',
                'price': 999.99,
                'original_price': 1199.99,
                'category': 'laptops',
                'source': 'amazon',
                'rating': 4.7,
                'num_reviews': 12456,
                'affiliate_url': 'https://amazon.com/dp/B0CX23V2ZK',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/71jG+e7roXL._AC_SL1500_.jpg'
            },
            {
                'title': 'Sony WH-1000XM5 Wireless Headphones',
                'description': 'Industry-leading noise canceling, 30-hour battery life, crystal clear hands-free calling',
                'price': 329.99,
                'original_price': 399.99,
                'category': 'headphones',
                'source': 'amazon',
                'rating': 4.4,
                'num_reviews': 9876,
                'affiliate_url': 'https://amazon.com/dp/B09XS7JWHH',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/51QeS0jZerL._AC_SL1500_.jpg'
            },
            {
                'title': 'iPad Pro 11-inch M4 256GB',
                'description': 'Ultra Retina XDR display, M4 chip, supports Apple Pencil Pro, Space Black',
                'price': 899.99,
                'original_price': 999.99,
                'category': 'electronics',
                'source': 'amazon',
                'rating': 4.8,
                'num_reviews': 5432,
                'affiliate_url': 'https://amazon.com/dp/B0D3J9XDMQ',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61uA2UVnYWL._AC_SL1500_.jpg'
            },
            {
                'title': 'ASUS ROG Strix Gaming Laptop',
                'description': 'RTX 4060 8GB, AMD Ryzen 7 7735HS, 16GB DDR5, 512GB SSD, 15.6" 144Hz display',
                'price': 1199.99,
                'original_price': 1399.99,
                'category': 'gaming',
                'source': 'amazon',
                'rating': 4.3,
                'num_reviews': 3421,
                'affiliate_url': 'https://amazon.com/dp/B0C789JBQX',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/81bc8mA3nKL._AC_SL1500_.jpg'
            },
            {
                'title': 'Amazon Echo Dot (5th Gen)',
                'description': 'Smart speaker with Alexa, improved audio, temperature sensor, Charcoal',
                'price': 39.99,
                'original_price': 49.99,
                'category': 'smart-home',
                'source': 'amazon',
                'rating': 4.2,
                'num_reviews': 87654,
                'affiliate_url': 'https://amazon.com/dp/B09B8V1LZ3',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg'
            },
            {
                'title': 'Anker PowerCore 10000 Portable Charger',
                'description': 'Ultra-compact 10000mAh power bank, high-speed charging, PowerIQ technology',
                'price': 19.99,
                'original_price': 29.99,
                'category': 'accessories',
                'source': 'amazon',
                'rating': 4.6,
                'num_reviews': 45321,
                'affiliate_url': 'https://amazon.com/dp/B019GJLER8',
                'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61V8f2VT1uL._AC_SL1500_.jpg'
            }
        ]
        
        # Clear existing sample deals
        Deal.query.filter_by(source='sample').delete()
        
        for deal_data in sample_deals:
            # Calculate discount percentage
            if deal_data.get('original_price') and deal_data.get('price'):
                discount = int(((deal_data['original_price'] - deal_data['price']) / deal_data['original_price']) * 100)
                deal_data['discount_percentage'] = discount
            
            # Generate AI headline
            try:
                ai_headline = self.ai_service.generate_deal_headline(
                    deal_data['title'],
                    deal_data['price'],
                    deal_data.get('original_price'),
                    deal_data['category']
                )
                deal_data['ai_headline'] = ai_headline
            except Exception as e:
                logging.warning(f"Failed to generate AI headline for {deal_data['title']}: {e}")
                deal_data['ai_headline'] = f"🔥 Great Deal on {deal_data['title']}!"
            
            # Set expiration date (7 days from now)
            deal_data['expires_at'] = datetime.utcnow() + timedelta(days=7)
            deal_data['source'] = 'sample'
            
            deal = Deal(**deal_data)
            db.session.add(deal)
        
        db.session.commit()
        logging.info(f"Generated {len(sample_deals)} sample deals")
