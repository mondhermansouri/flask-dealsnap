import requests
import logging
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from app import db
from models import Deal
from ai_service import AIService

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

class ScraperService:
    def __init__(self):
        self.ai_service = AIService()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_deal_from_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single deal from a given URL
        Supports Amazon, Best Buy, Newegg and other major retailers
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine the retailer and use appropriate scraping logic
            if 'amazon.com' in url:
                return self._scrape_amazon(soup, url)
            elif 'bestbuy.com' in url:
                return self._scrape_bestbuy(soup, url)
            elif 'newegg.com' in url:
                return self._scrape_newegg(soup, url)
            else:
                return self._scrape_generic(soup, url)
                
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return None
    
    def _scrape_amazon(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Amazon product page"""
        deal = {}
        
        # Title
        title_selectors = [
            '#productTitle',
            '.product-title',
            'h1.a-size-large'
        ]
        deal['title'] = self._extract_text(soup, title_selectors)
        
        # Price
        price_selectors = [
            '.a-price .a-offscreen',
            '.a-price-whole',
            '#price_inside_buybox'
        ]
        price_text = self._extract_text(soup, price_selectors)
        deal['price'] = self._extract_price(price_text)
        
        # Original price (for discounts)
        original_price_selectors = [
            '.a-price.a-text-price .a-offscreen',
            '.a-price-was .a-offscreen'
        ]
        original_price_text = self._extract_text(soup, original_price_selectors)
        deal['original_price'] = self._extract_price(original_price_text)
        
        # Description
        desc_selectors = [
            '#feature-bullets ul',
            '#productDescription',
            '.a-spacing-medium .a-size-base'
        ]
        deal['description'] = self._extract_text(soup, desc_selectors)[:500]
        
        # Image
        img_selectors = [
            '#landingImage',
            '.a-dynamic-image',
            '#imgTagWrapperId img'
        ]
        deal['image_url'] = self._extract_image(soup, img_selectors, url)
        
        # Rating
        rating_selectors = [
            '.a-icon-alt',
            '.cr-widget-FocalReviews .a-icon-alt'
        ]
        rating_text = self._extract_text(soup, rating_selectors)
        deal['rating'] = self._extract_rating(rating_text)
        
        # Reviews count
        reviews_selectors = [
            '#acrCustomerReviewText',
            '.cr-widget-FocalReviews .a-size-base'
        ]
        reviews_text = self._extract_text(soup, reviews_selectors)
        deal['num_reviews'] = self._extract_number(reviews_text)
        
        deal['source'] = 'amazon'
        deal['affiliate_url'] = url
        
        return deal
    
    def _scrape_bestbuy(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Best Buy product page"""
        deal = {}
        
        deal['title'] = self._extract_text(soup, ['.heading-5.v-fw-regular', 'h1'])
        
        # Price
        price_text = self._extract_text(soup, ['.sr-only:contains("current price")', '.screen-reader-only'])
        deal['price'] = self._extract_price(price_text)
        
        # Original price
        original_price_text = self._extract_text(soup, ['.pricing-price__regular-price'])
        deal['original_price'] = self._extract_price(original_price_text)
        
        deal['description'] = self._extract_text(soup, ['.product-data-value'])[:500]
        deal['image_url'] = self._extract_image(soup, ['.primary-image'], url)
        
        # Rating
        rating_text = self._extract_text(soup, ['.c-ratings-reviews .sr-only'])
        deal['rating'] = self._extract_rating(rating_text)
        
        deal['source'] = 'bestbuy'
        deal['affiliate_url'] = url
        
        return deal
    
    def _scrape_newegg(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Newegg product page"""
        deal = {}
        
        deal['title'] = self._extract_text(soup, ['.product-title', 'h1'])
        
        # Price
        price_text = self._extract_text(soup, ['.price-current', '.product-price .price'])
        deal['price'] = self._extract_price(price_text)
        
        # Original price
        original_price_text = self._extract_text(soup, ['.price-was'])
        deal['original_price'] = self._extract_price(original_price_text)
        
        deal['description'] = self._extract_text(soup, ['.product-bullets'])[:500]
        deal['image_url'] = self._extract_image(soup, ['.product-view-img'], url)
        
        deal['source'] = 'newegg'
        deal['affiliate_url'] = url
        
        return deal
    
    def _scrape_generic(self, soup: BeautifulSoup, url: str) -> Dict:
        """Generic scraper for unknown sites"""
        deal = {}
        
        # Use Open Graph and schema.org data
        deal['title'] = (
            self._extract_meta(soup, 'og:title') or
            self._extract_text(soup, ['h1', '.product-title', '.title'])
        )
        
        deal['description'] = (
            self._extract_meta(soup, 'og:description') or
            self._extract_text(soup, ['.description', '.product-description'])[:500]
        )
        
        deal['image_url'] = (
            self._extract_meta(soup, 'og:image') or
            self._extract_image(soup, ['.product-image img', '.main-image'], url)
        )
        
        # Try to find price using common patterns
        price_text = self._extract_text(soup, [
            '.price', '.cost', '.amount', '[class*="price"]', '[id*="price"]'
        ])
        deal['price'] = self._extract_price(price_text)
        
        deal['source'] = urlparse(url).netloc
        deal['affiliate_url'] = url
        
        return deal
    
    def _extract_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text from first matching selector"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
    
    def _extract_meta(self, soup: BeautifulSoup, property_name: str) -> str:
        """Extract meta tag content"""
        meta = soup.find('meta', property=property_name) or soup.find('meta', attrs={'name': property_name})
        return meta.get('content', '') if meta else ''
    
    def _extract_image(self, soup: BeautifulSoup, selectors: List[str], base_url: str) -> str:
        """Extract image URL from first matching selector"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                src = element.get('src') or element.get('data-src')
                if src:
                    return urljoin(base_url, src)
        return ""
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        
        # Remove common currency symbols and find numbers
        price_match = re.search(r'[\$£€¥]?([0-9,]+\.?[0-9]*)', text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group(1).replace(',', ''))
            except ValueError:
                pass
        return None
    
    def _extract_rating(self, text: str) -> Optional[float]:
        """Extract rating from text"""
        if not text:
            return None
        
        rating_match = re.search(r'([0-9\.]+)\s*(?:out of|\/)\s*5', text)
        if rating_match:
            try:
                return float(rating_match.group(1))
            except ValueError:
                pass
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text (for review counts)"""
        if not text:
            return None
        
        number_match = re.search(r'([0-9,]+)', text.replace(',', ''))
        if number_match:
            try:
                return int(number_match.group(1).replace(',', ''))
            except ValueError:
                pass
        return None
    
    def categorize_product(self, title: str, description: str) -> str:
        """Automatically categorize product based on title and description"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['phone', 'smartphone', 'iphone', 'android', 'mobile']):
            return 'smartphones'
        elif any(word in text for word in ['laptop', 'macbook', 'notebook', 'computer']):
            return 'laptops'
        elif any(word in text for word in ['headphone', 'earphone', 'airpods', 'speaker', 'audio']):
            return 'headphones'
        elif any(word in text for word in ['gaming', 'xbox', 'playstation', 'nintendo', 'game']):
            return 'gaming'
        elif any(word in text for word in ['smart home', 'alexa', 'echo', 'nest', 'iot']):
            return 'smart-home'
        elif any(word in text for word in ['cable', 'charger', 'case', 'adapter', 'accessory']):
            return 'accessories'
        else:
            return 'electronics'
    
    def add_deal_from_url(self, url: str, featured: bool = False) -> bool:
        """
        Scrape a deal from URL and add it to the database
        """
        try:
            deal_data = self.scrape_deal_from_url(url)
            if not deal_data or not deal_data.get('title'):
                return False
            
            # Calculate discount if both prices available
            if deal_data.get('original_price') and deal_data.get('price'):
                discount = int(((deal_data['original_price'] - deal_data['price']) / deal_data['original_price']) * 100)
                deal_data['discount_percentage'] = discount
            
            # Auto-categorize
            deal_data['category'] = self.categorize_product(
                deal_data.get('title', ''), 
                deal_data.get('description', '')
            )
            
            # Generate AI headline
            try:
                ai_headline = self.ai_service.generate_deal_headline(
                    deal_data['title'],
                    deal_data.get('price'),
                    deal_data.get('original_price'),
                    deal_data['category']
                )
                deal_data['ai_headline'] = ai_headline
            except Exception as e:
                logging.warning(f"Failed to generate AI headline: {e}")
                deal_data['ai_headline'] = f"🔥 Great Deal on {deal_data['title']}!"
            
            # Set other fields
            deal_data['featured'] = featured
            deal_data['is_active'] = True
            
            # Create and save deal
            deal = Deal(**deal_data)
            db.session.add(deal)
            db.session.commit()
            
            logging.info(f"Added deal: {deal_data['title']}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding deal from {url}: {e}")
            return False
    
    def bulk_scrape_from_urls(self, urls: List[str]) -> Dict[str, int]:
        """
        Scrape multiple URLs and return success/failure counts
        """
        results = {'success': 0, 'failed': 0}
        
        for url in urls:
            if self.add_deal_from_url(url):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results