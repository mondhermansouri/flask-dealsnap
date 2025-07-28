import os
import json
import logging
from openai import OpenAI

class AIService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_deal_headline(self, title, price, original_price=None, category="electronics"):
        """Generate a catchy AI headline for a deal"""
        if not self.client:
            # Fallback if no API key
            discount_text = ""
            if original_price and price < original_price:
                discount = int(((original_price - price) / original_price) * 100)
                discount_text = f"Save {discount}% - "
            
            return f"🔥 {discount_text}{title} - Limited Time!"
        
        try:
            # Calculate discount if available
            discount_info = ""
            if original_price and price < original_price:
                discount = int(((original_price - price) / original_price) * 100)
                discount_info = f"with {discount}% off (was ${original_price:.2f}, now ${price:.2f})"
            else:
                discount_info = f"at ${price:.2f}"
            
            prompt = f"""Generate a catchy, engaging headline for this tech deal that will make people want to click and buy. 
            
            Product: {title}
            Category: {category}
            Price: {discount_info}
            
            Requirements:
            - Start with an emoji (🔥, ⚡, 💥, 🎯, ✨, etc.)
            - Keep it under 100 characters
            - Create urgency and excitement
            - Highlight the savings or value
            - Make it feel exclusive
            - Sound natural and appealing
            
            Return only the headline text, nothing else."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            headline = response.choices[0].message.content.strip()
            return headline
            
        except Exception as e:
            logging.error(f"Error generating AI headline: {e}")
            # Fallback headline
            discount_text = ""
            if original_price and price < original_price:
                discount = int(((original_price - price) / original_price) * 100)
                discount_text = f"Save {discount}% - "
            
            return f"🔥 {discount_text}{title} - Limited Time Deal!"
    
    def generate_deal_description(self, title, category, features=None):
        """Generate an enhanced product description"""
        if not self.client:
            return f"Amazing {category} deal on {title}. Don't miss out!"
        
        try:
            features_text = f"Features: {', '.join(features)}" if features else ""
            
            prompt = f"""Write a compelling product description for this tech deal:
            
            Product: {title}
            Category: {category}
            {features_text}
            
            Make it:
            - 2-3 sentences maximum
            - Highlight key benefits
            - Create desire to purchase
            - Professional but exciting tone
            
            Return only the description text."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating description: {e}")
            return f"Premium {category} with exceptional value. Limited time offer!"
