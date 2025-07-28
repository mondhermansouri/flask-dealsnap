from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Deal, ClickEvent
from deal_service import DealService
from ai_service import AIService
from scraper_service import ScraperService
from datetime import datetime
import logging

deal_service = DealService()
ai_service = AIService()
scraper_service = ScraperService()

@app.route('/')
def index():
    """Main page showing featured and recent deals"""
    category = request.args.get('category', 'all')
    
    # Get featured deals
    featured_deals = Deal.query.filter_by(is_active=True, featured=True).limit(5).all()
    
    # Get deals by category
    if category == 'all':
        deals = Deal.query.filter_by(is_active=True).order_by(Deal.created_at.desc()).limit(20).all()
    else:
        deals = Deal.query.filter_by(is_active=True, category=category).order_by(Deal.created_at.desc()).limit(20).all()
    
    categories = ['all', 'electronics', 'smartphones', 'laptops', 'headphones', 'smart-home', 'gaming', 'accessories']
    
    return render_template('index.html', 
                         deals=deals, 
                         featured_deals=featured_deals,
                         categories=categories,
                         current_category=category)

@app.route('/deal/<int:deal_id>')
def deal_detail(deal_id):
    """Individual deal detail page"""
    deal = Deal.query.get_or_404(deal_id)
    
    # Increment view count
    deal.views += 1
    db.session.commit()
    
    # Get related deals from same category
    related_deals = Deal.query.filter(
        Deal.category == deal.category,
        Deal.id != deal.id,
        Deal.is_active == True
    ).limit(4).all()
    
    return render_template('deal_detail.html', deal=deal, related_deals=related_deals)

@app.route('/click/<int:deal_id>')
def click_deal(deal_id):
    """Track click and redirect to affiliate URL"""
    deal = Deal.query.get_or_404(deal_id)
    
    # Track click event
    click_event = ClickEvent(
        deal_id=deal.id,
        ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        user_agent=request.headers.get('User-Agent'),
        referrer=request.headers.get('Referer')
    )
    
    # Increment click count
    deal.clicks += 1
    
    db.session.add(click_event)
    db.session.commit()
    
    # Create a redirect page that opens in new window to avoid iframe restrictions
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirection vers {deal.title}</title>
        <meta charset="UTF-8">
        <script>
            // Open in new window/tab to avoid iframe restrictions
            window.open('{deal.affiliate_url}', '_blank');
            // Close current window if it was opened by JavaScript
            setTimeout(function() {{
                window.close();
                // If we can't close, redirect in current window as fallback
                window.location.href = '{deal.affiliate_url}';
            }}, 1000);
        </script>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .container {{ max-width: 500px; margin: 0 auto; }}
            .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="spinner"></div>
            <h2>Redirection en cours...</h2>
            <p>Vous allez être redirigé vers <strong>{deal.title}</strong></p>
            <p>Si la redirection ne fonctionne pas automatiquement, <a href="{deal.affiliate_url}" target="_blank">cliquez ici</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/admin')
def admin():
    """Admin dashboard for managing deals"""
    deals = Deal.query.order_by(Deal.created_at.desc()).all()
    
    # Calculate analytics
    total_deals = Deal.query.count()
    active_deals = Deal.query.filter_by(is_active=True).count()
    total_clicks = db.session.query(db.func.sum(Deal.clicks)).scalar() or 0
    total_views = db.session.query(db.func.sum(Deal.views)).scalar() or 0
    
    analytics = {
        'total_deals': total_deals,
        'active_deals': active_deals,
        'total_clicks': total_clicks,
        'total_views': total_views,
        'ctr': (total_clicks / total_views * 100) if total_views > 0 else 0
    }
    
    return render_template('admin.html', deals=deals, analytics=analytics)

@app.route('/admin/generate-sample-deals')
def generate_sample_deals():
    """Generate sample deals with AI headlines"""
    try:
        deal_service.generate_sample_deals()
        flash('Sample deals generated successfully!', 'success')
    except Exception as e:
        logging.error(f"Error generating sample deals: {e}")
        flash(f'Error generating deals: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/regenerate-headlines')
def regenerate_headlines():
    """Regenerate AI headlines for all deals"""
    try:
        deals = Deal.query.filter_by(is_active=True).all()
        for deal in deals:
            headline = ai_service.generate_deal_headline(
                deal.title, 
                deal.price, 
                deal.original_price, 
                deal.category
            )
            deal.ai_headline = headline
        
        db.session.commit()
        flash(f'Regenerated headlines for {len(deals)} deals!', 'success')
    except Exception as e:
        logging.error(f"Error regenerating headlines: {e}")
        flash(f'Error regenerating headlines: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/scrape-deal', methods=['POST'])
def scrape_deal():
    """Add a deal by scraping from URL"""
    url = request.form.get('url')
    featured = request.form.get('featured') == 'on'
    
    if not url:
        flash('Please provide a URL', 'error')
        return redirect(url_for('admin'))
    
    try:
        success = scraper_service.add_deal_from_url(url, featured=featured)
        if success:
            flash('Deal added successfully!', 'success')
        else:
            flash('Failed to scrape deal from URL', 'error')
    except Exception as e:
        logging.error(f"Error scraping deal: {e}")
        flash(f'Error scraping deal: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/add-deal', methods=['GET', 'POST'])
def add_deal():
    """Add deal manually"""
    if request.method == 'GET':
        return render_template('add_deal.html')
    
    try:
        # Get form data
        title = request.form.get('title')
        ai_headline = request.form.get('ai_headline')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        original_price_str = request.form.get('original_price')
        original_price = float(original_price_str) if original_price_str else None
        category = request.form.get('category')
        source = request.form.get('source')
        affiliate_url = request.form.get('affiliate_url')
        image_url = request.form.get('image_url')
        rating_str = request.form.get('rating')
        rating = float(rating_str) if rating_str else None
        num_reviews_str = request.form.get('num_reviews')
        num_reviews = int(num_reviews_str) if num_reviews_str else None
        expires_at_str = request.form.get('expires_at')
        expires_at = datetime.strptime(expires_at_str, '%Y-%m-%dT%H:%M') if expires_at_str else None
        featured = 'featured' in request.form
        is_active = 'is_active' in request.form
        
        # Calculate discount percentage
        discount_percentage = None
        if original_price and original_price > price:
            discount_percentage = int(((original_price - price) / original_price) * 100)
        
        # Create deal
        deal = Deal(
            title=title,
            description=description,
            price=price,
            original_price=original_price,
            discount_percentage=discount_percentage,
            affiliate_url=affiliate_url,
            image_url=image_url,
            category=category,
            source=source,
            rating=rating,
            num_reviews=num_reviews,
            expires_at=expires_at,
            featured=featured,
            is_active=is_active
        )
        
        # Generate AI headline if not provided
        if ai_headline:
            deal.ai_headline = ai_headline
        else:
            try:
                ai_headline = ai_service.generate_deal_headline(
                    deal.title,
                    deal.price,
                    deal.original_price,
                    deal.category
                )
                deal.ai_headline = ai_headline
            except Exception as e:
                logging.warning(f"Failed to generate AI headline: {e}")
                discount_text = f" - {discount_percentage}% OFF!" if discount_percentage else ""
                deal.ai_headline = f"🔥 Amazing Deal: {deal.title}{discount_text}"
        
        db.session.add(deal)
        db.session.commit()
        
        flash(f'Deal "{deal.title}" added successfully!', 'success')
        return redirect(url_for('admin'))
        
    except Exception as e:
        logging.error(f"Error adding deal: {e}")
        flash(f'Error adding deal: {str(e)}', 'error')
        return render_template('add_deal.html')

# API Routes
@app.route('/api/deals')
def api_deals():
    """API endpoint for deals - for future mobile app"""
    category = request.args.get('category', 'all')
    limit = min(int(request.args.get('limit', 20)), 100)
    
    query = Deal.query.filter_by(is_active=True)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    deals = query.order_by(Deal.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'deals': [deal.to_dict() for deal in deals],
        'total': len(deals),
        'category': category
    })

@app.route('/api/deal/<int:deal_id>')
def api_deal_detail(deal_id):
    """API endpoint for single deal"""
    deal = Deal.query.get_or_404(deal_id)
    
    # Increment view count
    deal.views += 1
    db.session.commit()
    
    return jsonify(deal.to_dict())

@app.route('/api/categories')
def api_categories():
    """API endpoint for available categories"""
    categories = ['electronics', 'smartphones', 'laptops', 'headphones', 'smart-home', 'gaming', 'accessories']
    return jsonify({'categories': categories})

# Enhanced API endpoints for mobile apps
@app.route('/api/deals/featured')
def api_featured_deals():
    """API endpoint for featured deals only"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    deals = Deal.query.filter_by(is_active=True, featured=True).order_by(Deal.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'deals': [deal.to_dict() for deal in deals],
        'total': len(deals)
    })

@app.route('/api/deals/trending')
def api_trending_deals():
    """API endpoint for trending deals (most clicked)"""
    limit = min(int(request.args.get('limit', 20)), 50)
    
    deals = Deal.query.filter_by(is_active=True).order_by(Deal.clicks.desc(), Deal.views.desc()).limit(limit).all()
    
    return jsonify({
        'deals': [deal.to_dict() for deal in deals],
        'total': len(deals)
    })

@app.route('/api/deals/search')
def api_search_deals():
    """API endpoint for searching deals"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 50)
    
    if not query:
        return jsonify({'deals': [], 'total': 0, 'query': query})
    
    # Search in title, AI headline, and description
    deals = Deal.query.filter(
        Deal.is_active == True
    ).filter(
        db.or_(
            Deal.title.ilike(f'%{query}%'),
            Deal.ai_headline.ilike(f'%{query}%'),
            Deal.description.ilike(f'%{query}%')
        )
    ).order_by(Deal.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'deals': [deal.to_dict() for deal in deals],
        'total': len(deals),
        'query': query
    })

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for basic analytics"""
    total_deals = Deal.query.count()
    active_deals = Deal.query.filter_by(is_active=True).count()
    total_clicks = db.session.query(db.func.sum(Deal.clicks)).scalar() or 0
    total_views = db.session.query(db.func.sum(Deal.views)).scalar() or 0
    
    # Top categories
    category_stats = db.session.query(
        Deal.category,
        db.func.count(Deal.id).label('count'),
        db.func.sum(Deal.clicks).label('total_clicks')
    ).filter_by(is_active=True).group_by(Deal.category).all()
    
    return jsonify({
        'total_deals': total_deals,
        'active_deals': active_deals,
        'total_clicks': total_clicks,
        'total_views': total_views,
        'ctr': (total_clicks / total_views * 100) if total_views > 0 else 0,
        'categories': [
            {
                'name': cat[0],
                'deal_count': cat[1],
                'total_clicks': cat[2] or 0
            }
            for cat in category_stats
        ]
    })

@app.route('/api/deals/price-range')
def api_deals_by_price():
    """API endpoint for deals within price range"""
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', 10000))
    category = request.args.get('category', 'all')
    limit = min(int(request.args.get('limit', 20)), 50)
    
    query = Deal.query.filter(
        Deal.is_active == True,
        Deal.price >= min_price,
        Deal.price <= max_price
    )
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    deals = query.order_by(Deal.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'deals': [deal.to_dict() for deal in deals],
        'total': len(deals),
        'filters': {
            'min_price': min_price,
            'max_price': max_price,
            'category': category
        }
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html'), 500
