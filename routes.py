from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Deal, ClickEvent
from deal_service import DealService
from ai_service import AIService
from scraper_service import ScraperService
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
    
    return redirect(deal.affiliate_url)

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
