# DealSnap - AI-Curated Tech Deals Platform

## Overview

DealSnap is a Flask-based web application that aggregates and displays tech deals with AI-generated headlines. The platform features a modern, responsive design with Progressive Web App (PWA) capabilities, allowing users to browse curated deals across various technology categories.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via DATABASE_URL environment variable
- **AI Integration**: OpenAI API for generating catchy deal headlines
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0 (CDN)
- **Icons**: Font Awesome 6.4.0 (CDN)
- **Progressive Web App**: Service worker, manifest, and offline capabilities
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Application Structure
```
/
├── app.py              # Flask app initialization and configuration
├── main.py             # Application entry point
├── models.py           # Database models (Deal, ClickEvent)
├── routes.py           # URL routing and view functions
├── deal_service.py     # Business logic for deal management
├── ai_service.py       # OpenAI integration for headline generation
├── static/             # Static assets (CSS, JS, manifest, service worker)
└── templates/          # HTML templates
```

## Key Components

### Database Schema (SQLAlchemy Models)
- **Deal Model**: Primary entity storing deal information including title, price, images, categories, analytics data, and AI-generated headlines
- **ClickEvent Model**: Analytics tracking for user interactions (referenced but not fully implemented)

### AI Service
- **Headline Generation**: Uses OpenAI GPT-4o API to create engaging, emoji-enhanced headlines for deals
- **Fallback Strategy**: Provides basic headline generation when API key is unavailable
- **Dynamic Prompting**: Customizes prompts based on discount percentage and product category

### Deal Service
- **Sample Data Generation**: Creates realistic tech deal data for testing and demonstration
- **Category Management**: Handles multiple product categories (smartphones, laptops, headphones, etc.)
- **Business Logic**: Manages deal lifecycle and data processing

### Scraper Service (NEW)
- **Multi-Platform Scraping**: Supports Amazon, Best Buy, Newegg, and generic websites
- **Automatic Categorization**: AI-powered product categorization based on title and description
- **Price Detection**: Extracts regular and sale prices with discount calculation
- **Image & Rating Extraction**: Captures product images and customer ratings
- **Real-Time Integration**: Admin panel allows instant deal addition via URL

### PWA Features
- **Service Worker**: Caches resources for offline functionality
- **Web Manifest**: Defines app metadata, icons, and installation behavior
- **Install Prompts**: JavaScript handling for app installation

## Data Flow

1. **Deal Creation**: Deals are created via the DealService with sample data or external sources
2. **AI Enhancement**: Deal titles are processed through AIService to generate engaging headlines
3. **Database Storage**: Enhanced deals are stored in SQLAlchemy models
4. **Web Display**: Flask routes serve deals through Jinja2 templates
5. **User Interaction**: Analytics tracking for views and clicks
6. **PWA Installation**: Service worker enables offline access and app-like experience

## External Dependencies

### APIs
- **OpenAI API**: For AI headline generation (requires OPENAI_API_KEY environment variable)
- **Amazon Product Images**: Deal images sourced from Amazon CDN

### CDN Resources
- **Bootstrap 5.3.0**: UI framework and components
- **Font Awesome 6.4.0**: Icon library
- **External Fonts**: System fonts with fallbacks

### Environment Variables
- `OPENAI_API_KEY`: Required for AI headline generation
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SESSION_SECRET`: Flask session encryption key

## Deployment Strategy

### Production Considerations
- **Database**: Configured to use PostgreSQL in production via DATABASE_URL
- **WSGI**: ProxyFix middleware for proper header handling behind reverse proxies
- **Connection Pooling**: SQLAlchemy engine configured with connection recycling
- **CORS**: Enabled for API access from different origins

### Development Setup
- **Debug Mode**: Enabled in main.py for development
- **Auto-reload**: Flask development server with automatic code reloading
- **Local Database**: SQLite fallback for development environments

### PWA Deployment
- **Service Worker**: Caches essential resources for offline functionality
- **Manifest**: Configured for app store submission and installation
- **HTTPS Required**: PWA features require secure connection in production

The application is designed to be easily deployable to platforms like Heroku, Railway, or any WSGI-compatible hosting service with minimal configuration changes.